export default {
  async fetch(request, env) {
    if (request.method === "POST") {
      const data = await request.json();

      await env.DB.prepare(`
        INSERT INTO bookings
        (name, phone, stay_type, checkin_date, checkout_date, note)
        VALUES (?, ?, ?, ?, ?, ?)
      `)
      .bind(
        data.name,
        data.phone,
        data.stay_type,
        data.checkin_date,
        data.checkout_date,
        data.note
      )
      .run();

      return Response.json({ success: true });
    }

    return new Response("API Running");
  }
}
