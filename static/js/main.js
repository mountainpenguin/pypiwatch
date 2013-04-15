var progressBarMouseDown = false;
var totalSeconds;

$(document).ready(function(){
    totalSeconds = parseInt($("#progress-length").data("seconds"));
    $(".watch-item").click( function (evt) {
        evt.preventDefault();
        var itemID = $(this).attr("id").split("watch-item-")[1];
        $.ajax({
            url: "/ajax",
            data: {
                command: "playable",
                itemID: itemID
            },
            success: function (data) {
                var playable = data.playable;
                var modal = $("#watch-item-modal-template").clone();
                modal.attr("id", "");
                var modalbody = modal.find(".modal-body");
                if (playable.length > 0) {
                    for (i=0; i<playable.length; i++) {
                        var play = playable[i];
                        var itemtempl = modal.find("#watch-item-watchable-template").clone().attr("id","");
                        itemtempl.find(".watch-this-item").data({
                            itemID: itemID,
                            itemindex: i
                        }).click(watchFunc);
                        itemtempl.find(".dirname").html(play[0]);
                        itemtempl.find(".basename").html(play[1]);
                        modalbody.append(itemtempl);
                    }
                } else {
                    modalbody.append($("<p>No viewable files</p>"));
                }
                modal.find("#watch-item-watchable-template").remove();
                modal.modal();
            }
        });
    });
    $("#pause-playing").click( function (evt) {
        $.ajax({
            url: "/ajax",
            data: {
                command: "pause"
            },
            success: function(data) {
                if (data.status == "playing") {
                    $("#pause-playing").html("Pause").toggleClass("btn-warning btn-success");
                } else {
                    $("#pause-playing").html("Play").toggleClass("btn-warning btn-success");
                }
            }
        });
    });
    $("#stop-playing").click( function (evt) {
        $.ajax({
            url: "/ajax",
            data: {
                command: "stop"
            },
            success: function(data) {
                location.reload();
            }
        });
    });
    $("#progress-slider").slider()
                         .on("slideStart", slideStart)
                         .on("slide", slideUpdate)
                         .on("slideStop", slideStop); 

    progressFunc();
    window.setInterval(progressFunc, 2000);
});

function slideStart(evt) {
    progressBarMouseDown = true;
    $(".slider-selection").addClass("seeking");
    $("#progress-current").addClass("seeking");
}

function slideUpdate(evt) {
    var percentage = evt.value;
    $("#progress-current").html(
        secondsToHumanStamp(calculateSeconds(percentage))
    );
}

function slideStop(evt) {
    progressBarMouseDown = false;
    $(".slider-selection").removeClass("seeking");
    $("#progress-current").removeClass("seeking");
    var percentage = evt.value;
    $.ajax({
        url: "/ajax",
        data: {
            command: "seek",
            seconds: calculateSeconds(percentage)
        },
        success: function (data) {
            $("#progress-current").html(secondsToHumanStamp(calculateSeconds(percentage)));
            $("#progress-slider").slider("setValue", percentage);
        }
    });
}

function progressFunc() {
    if (progressBarMouseDown) {
    } else {
        $.ajax({
            url: "/ajax",
            data: {
                command: "progress"
            },
            success: function (data) {
                if (data.progress) {
                    $("#progress-current").html(data.progress);
                    $("#progress-slider").slider("setValue", data.percentage);
                }
            }
        });
    }
}

function watchFunc(evt) {
    evt.preventDefault();
    $.ajax({
        url: "/ajax",
        data: {
            command: "play",
            itemID: $(this).data("itemID"),
            itemindex: $(this).data("itemindex")
        },
        success: function (data) {
            location.reload();
        }
    });
}

function calculateSeconds(percentage) {
    var perc = parseInt(percentage);
    return totalSeconds * perc / 100;
}

function secondsToHumanStamp(seconds) {
    var hours = parseInt(seconds / (60*60));
    seconds -= hours*60*60;
    var minutes = parseInt(seconds / 60);
    seconds -= minutes*60;
    seconds = parseInt(seconds).toString();
    var fmt = "";
    hours = hours.toString();
    minutes = minutes.toString();
    if (hours.length == 1) {
        fmt += "0" + hours + ":";
    } else {
        fmt += hours + ":";
    }
    if (minutes.length == 1) {
        fmt += "0" + minutes + ":";
    } else {
        fmt += minutes + ":";
    }
    if (seconds.length == 1) {
        fmt += "0" + seconds;
    } else {
        fmt += seconds;
    }
    return fmt;
}
