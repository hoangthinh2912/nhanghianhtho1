export async function onRequestPost(context) {
  const { request, env } = context;

  try {
    const data = await request.json();

    await env.DB.prepare(`
      INSERT INTO bookings
      (customer_name, phone, room_type, checkin_date, note)
      VALUES (?, ?, ?, ?, ?)
    `)
    .bind(
      data.customer_name,
      data.phone,
      data.room_type,
      data.checkin_date,
      data.note
    )
    .run();

    return Response.json({
      success: true,
      message: "Đặt phòng thành công"
    });

  } catch (error) {
    return Response.json({
      success: false,
      error: error.message
    }, {
      status: 500
    });
  }
}
