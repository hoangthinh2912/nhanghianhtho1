async function datPhong() {
  const data = {
    customer_name: document.getElementById("customer_name").value,
    phone: document.getElementById("phone").value,
    room_type: document.getElementById("room_type").value,
    checkin_date: document.getElementById("checkin_date").value,
    note: document.getElementById("note").value
  };

  const response = await fetch("/bookings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  const result = await response.json();

  if (result.success) {
    alert("Đặt phòng thành công!");
  } else {
    alert("Lỗi: " + result.error);
  }
}
