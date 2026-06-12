export async function onRequestPost(context) {
  const { request, env } = context;

  const data = await request.json();

  await env.DB.prepare(`
    INSERT INTO bookings
    (fullname, phone, room)
    VALUES (?, ?, ?)
  `)
  .bind(
    data.fullname,
    data.phone,
    data.room
  )
  .run();

  return Response.json({
    success: true
  });
}
