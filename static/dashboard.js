setInterval(() => {

fetch("/api/monitoring")

.then(res => res.json())

.then(data => {

document.getElementById("cpu").innerHTML =
data.cpu_usage;

document.getElementById("ram").innerHTML =
data.ram_usage;

document.getElementById("disk").innerHTML =
data.disk_usage;

document.getElementById("swap").innerHTML =
data.swap_usage;

document.getElementById("users").innerHTML =
data.active_users;

});

},3000);
