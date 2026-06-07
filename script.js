const carPrices = {
    "Toyota Vios":700000,
    "Hyundai Accent":750000,
    "Kia Seltos":1100000
};

const params = new URLSearchParams(window.location.search);

const car = params.get("car");

if(car){
    document.getElementById("selectedCar").value = car;
}

function calculatePrice(){

    const car =
        document.getElementById("selectedCar").value;

    const pickup =
        document.getElementById("pickupDate").value;

    const returnDate =
        document.getElementById("returnDate").value;

    if(!pickup || !returnDate || !car){
        return;
    }

    const start = new Date(pickup);
    const end = new Date(returnDate);

    if(end <= start){
        document.getElementById("totalPrice").innerHTML =
        "Ngày trả phải lớn hơn ngày nhận";
        return;
    }

    const days =
        Math.ceil((end-start)/(1000*60*60*24));

    const total =
        days * carPrices[car];

    document.getElementById("totalPrice").innerHTML =
    "Tổng tiền: " +
    total.toLocaleString("vi-VN") +
    " đ";
}

function submitBooking(){

    alert("Đặt xe thành công!");
}
