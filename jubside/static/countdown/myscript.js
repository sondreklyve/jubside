// Countdown code
var dateDiff ={

	timer: function(d1,d2){
		var t2 = d2.getTime();
		var t1 = d1.getTime();

		var days = (t2-t1)/(24*3600*1000)
		var remainDays = days % 1

		var hour = (remainDays*24)
		var remainHours = hour % 1

		var min = (remainHours*60)
		var remainMin = min % 1

		var sec = (remainMin*60)

		return [parseInt(days), parseInt(hour), parseInt(min), parseInt(sec)];
	}
}

// Time until Jubilee begins
function timeUntil(timeGoal){
	var localTime = new Date();

	var tv = dateDiff.timer(localTime,timeGoal);

	for (var i = tv.length - 1; i >= 0; i--) {
		if (tv[i] < 0){
			tv[i] = 0;
		}
	}

	let weeks = String(Math.floor(tv[0] / 7))

	var temp;
	for (var i = 0; i < tv.length; i++) {
		if (String(tv[i]).length < 2) {
			tv[i] = "0" + String(tv[i]);
		}
	}

	document.title = "Jub om " + tv[0] + " " + pluralForm(Number(tv[0]), "dag") + "!";

	document.getElementById("day").innerHTML = tv[0];
	document.getElementById("hour").innerHTML = tv[1];
	document.getElementById("min").innerHTML = tv[2];
	document.getElementById("sec").innerHTML = tv[3];

	document.getElementById("dayText").innerHTML = pluralForm(Number(tv[0]),"dag");
	document.getElementById("hourText").innerHTML = pluralForm(Number(tv[1]),"time");
	document.getElementById("minText").innerHTML = pluralForm(Number(tv[2]),"minutt");
	document.getElementById("secText").innerHTML = pluralForm(Number(tv[3]),"sekund");
}

// Plural for text
function pluralForm(number, string) {
	if (number == 1){
		return string;
	}

	if (string == "time"){
		return "timer";
	}

	return (string + "er");
}
// Setting datetime for start of Jubilee
let dStringGoal = "03/10/2023 12:00:00"
var timeGoal = new Date(dStringGoal);

function runFunctionUntil() {
	timeUntil(timeGoal);
}

runFunctionUntil();
var t=setInterval(runFunctionUntil,1000);