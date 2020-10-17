document.addEventListener('DOMContentLoaded', function() {
        world();
        india();
}, false);

            function world()
            {
            world = "/index/globalData";
            fetch(world)
           .then(response => response.json())
           .then(json => {
                    document.getElementById("worldNewCases").innerHTML=json[3].toLocaleString();
                    document.getElementById("worldNewDeceases").innerHTML=json[4].toLocaleString();
                    document.getElementById("worldNewRecovered").innerHTML=json[5].toLocaleString();
                    document.getElementById("worldTotal").innerHTML=json[0].toLocaleString();
                    document.getElementById("worldDeceased").innerHTML=json[1].toLocaleString();
                    document.getElementById("worldRecovered").innerHTML=json[2].toLocaleString();
           })
            }
            function india()
            {
             india = "/index/india";
           fetch(india)
           .then(response => response.json())
           .then(json => {
                    console.log(json);
                    document.getElementById("indTested").innerHTML=parseInt(json[0]).toLocaleString();
                    document.getElementById("indConfirmed").innerHTML=parseInt(json[1]).toLocaleString();
                    document.getElementById("indDeceased").innerHTML=parseInt(json[2]).toLocaleString();
                    document.getElementById("indRecovered").innerHTML=parseInt(json[3]).toLocaleString();
                    document.getElementById("indDeltaConfirmed").innerHTML=parseInt(json[4]).toLocaleString();
                    document.getElementById("indDeltaRecovered").innerHTML=parseInt(json[5]).toLocaleString();
                    document.getElementById("indDeltaDeaths").innerHTML=parseInt(json[6]).toLocaleString();
           })
            }