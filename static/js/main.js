$(document).ready(function(){
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

    
});

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
