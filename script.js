export default {
  async fetch(request, env) {

    if (request.method === "POST") {
      const data = await request.json();

      await env.DB.prepare(`
        INSERT INTO bookings
        (fullname, phone, room, stay_type, checkin_date, checkout_date, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `)
      .bind(
        data.fullname,
        data.phone,
        data.room,
        data.stay_type,
        data.checkin_date,
        data.checkout_date,
        data.note
      )
      .run();

      return Response.json({
        success: true
      });
    }

    return new Response("API Running");
  }
}
