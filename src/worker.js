const INITIAL_ROOMS = {
	standard: {
		key: "standard",
		name: "Phòng Tiêu chuẩn",
		type: "1-2 khách",
		price: 280000,
		note: "Phù hợp khách đi công tác hoặc lưu trú ngắn ngày cần chi phí hợp lý.",
		image: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200",
		amenities: ["Wifi miễn phí", "Máy lạnh", "Nước nóng"],
		available: 5,
		total: 5
	},
	family: {
		key: "family",
		name: "Phòng Gia đình",
		type: "3-4 khách",
		price: 420000,
		note: "Không gian rộng hơn, thích hợp cho gia đình nhỏ hoặc nhóm bạn đi cùng nhau.",
		image: "https://images.unsplash.com/photo-1560184897-ae75f418493e?w=1200",
		amenities: ["Giường lớn", "Bàn làm việc", "Khu ngồi nghỉ"],
		available: 5,
		total: 5
	},
	vip: {
		key: "vip",
		name: "Phòng Cao cấp",
		type: "2 khách",
		price: 560000,
		note: "Tối ưu cho khách muốn trải nghiệm thoải mái hơn với nội thất hài hòa.",
		image: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200",
		amenities: ["Không gian riêng tư", "Trang bị tốt hơn", "View thoáng"],
		available: 5,
		total: 5
	}
};

function cloneInitialRooms() {
	return Object.fromEntries(
		Object.entries(INITIAL_ROOMS).map(([key, room]) => [
			key,
			{
				...room,
				amenities: [...room.amenities]
			}
		])
	);
}

function json(data, init = {}) {
	return new Response(JSON.stringify(data), {
		...init,
		headers: {
			"content-type": "application/json; charset=utf-8",
			"cache-control": "no-store",
			...(init.headers || {})
		}
	});
}

function parseJsonDate(value) {
	const parsed = new Date(value);
	return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function createSnapshot(rooms, bookings) {
	return {
		type: "snapshot",
		rooms: Object.values(rooms).map((room) => ({
			...room,
			amenities: [...room.amenities]
		})),
		bookings: [...bookings],
		updatedAt: new Date().toISOString()
	};
}

export default {
	async fetch(request, env) {
		const url = new URL(request.url);

		if (url.pathname.startsWith("/api/")) {
			const roomStore = env.INVENTORY.get(env.INVENTORY.idFromName("main"));
			const apiPath = url.pathname.replace(/^\/api/, "") || "/";
			const proxiedRequest = new Request(`https://inventory${apiPath}${url.search}`, request);
			return roomStore.fetch(proxiedRequest);
		}

		return env.ASSETS.fetch(request);
	}
};

export class InventoryStore {
	constructor(state) {
		this.state = state;
		this.rooms = null;
		this.bookings = null;
		this.webSockets = new Set();
	}

	async load() {
		if (this.rooms && this.bookings) {
			return;
		}

		this.rooms = (await this.state.storage.get("rooms")) || cloneInitialRooms();
		this.bookings = (await this.state.storage.get("bookings")) || [];
	}

	async persist() {
		await this.state.storage.put("rooms", this.rooms);
		await this.state.storage.put("bookings", this.bookings);
	}

	currentSnapshot() {
		return createSnapshot(this.rooms, this.bookings);
	}

	broadcastSnapshot() {
		const payload = JSON.stringify(this.currentSnapshot());
		for (const socket of this.webSockets) {
			if (socket.readyState === 1) {
				socket.send(payload);
			}
		}
	}

	acceptSocket(socket) {
		socket.accept();
		this.webSockets.add(socket);
		socket.addEventListener("close", () => this.webSockets.delete(socket));
		socket.addEventListener("error", () => this.webSockets.delete(socket));
		socket.send(JSON.stringify(this.currentSnapshot()));
	}

	async createBooking(request) {
		const payload = await request.json();
		const roomKey = payload.roomKey;
		const room = this.rooms[roomKey];

		if (!room) {
			return json({ error: "Phòng không tồn tại" }, { status: 404 });
		}

		if (room.available <= 0) {
			return json({ error: "Phòng đã hết" }, { status: 409 });
		}

		const checkinDate = parseJsonDate(payload.checkin);
		const checkoutDate = parseJsonDate(payload.checkout);

		if (!checkinDate || !checkoutDate || checkoutDate <= checkinDate) {
			return json({ error: "Ngày nhận và ngày trả không hợp lệ" }, { status: 400 });
		}

		const days = Math.ceil((checkoutDate - checkinDate) / (1000 * 60 * 60 * 24));
		const total = days * room.price;

		room.available = Math.max(0, room.available - 1);
		const booking = {
			id: crypto.randomUUID(),
			roomKey,
			roomName: room.name,
			name: String(payload.name || ""),
			phone: String(payload.phone || ""),
			checkin: payload.checkin,
			checkout: payload.checkout,
			stayType: String(payload.stayType || "standard"),
			note: String(payload.note || ""),
			days,
			total,
			createdAt: new Date().toISOString()
		};

		this.bookings.unshift(booking);
		this.bookings = this.bookings.slice(0, 100);
		await this.persist();
		this.broadcastSnapshot();

		return json(this.currentSnapshot());
	}

	async fetch(request) {
		await this.load();
		const url = new URL(request.url);

		if (request.headers.get("Upgrade") === "websocket" && url.pathname === "/ws") {
			const pair = new WebSocketPair();
			const client = pair[0];
			const server = pair[1];
			this.acceptSocket(server);
			return new Response(null, { status: 101, webSocket: client });
		}

		if (url.pathname === "/rooms" && request.method === "GET") {
			return json(this.currentSnapshot());
		}

		if (url.pathname === "/bookings" && request.method === "GET") {
			return json(this.currentSnapshot());
		}

		if (url.pathname === "/bookings" && request.method === "POST") {
			return this.createBooking(request);
		}

		return new Response("Not Found", { status: 404 });
	}
}