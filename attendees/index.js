$(document).ready( function() {

    Eventbrite({'access_token': ""}, function(eb_client) {

        // Make map of member email -> array of events
        var member_events = {};
        (function make_member_events() {

            if (localStorage.member_events) {
                member_events = JSON.parse(localStorage.getItem("member_events"));
            } else {
                eb_client.user_list_events( {"only_display":"id,title,start_date"}, function( response ) { 
                    events = response.events;

                    $.each( events, function( index, e ) {
                        var eid = e.event.id;
                        var etitle = e.event.title;
                        var start = e.event.start_date;
                        // For each event, get attendees. 
                        eb_client.event_list_attendees( {'id': eid}, function( response ) {
                            // Add event to map using each attendee's email as name
                            var attendees = response.attendees;

                            $.each( attendees, function(index, attendee) {
                                var person = attendee.attendee;
                                var email = person.email;
                                var data = { "title":etitle, "start_date":start };
                                if (email in member_events) {
                                    member_events[email].push(data);
                                } else { 
                                    member_events[email] = [data];
                                }
                            });
                        });
                    });
                    localStorage.setItem("member_events", JSON.stringify(member_events));
                    console.log("member events done");
                });
            }
        })();

        $(".event-attendees input[type='submit']").click( function() {
            // Get list of attendees from eventbrite.
            var eb_id = $(".event-attendees input[name='eb_id']").val()
            var result_html = $("<div></div>");
            eb_client.event_list_attendees ( {'id': eb_id}, function( response ){
                var attendees = response.attendees;

                // For each attendee, show facebook picture, how many past total events
                $.each( attendees, function(index, attendee) {
                    var person = attendee.attendee;
                    var name = person.first_name + " " + person.last_name;
                    var email = person.email;
                    var events = member_events[email]; //TODO sort by date?
                    var select_html = $("<select></select>");
                    $.each( events, function(index, e) {
                        select_html.append("<option>" + e.title + "</option>");
                    });
                    var html = result_html.append(name + " ").append(events.length + " ").append(select_html).append("<br>");
                    $(".results").append(html); 
                });
            });
        });

        $(".dinner-series input[type='submit']").click( function() {
            // Get list of attendees from eventbrite.
            var eb_id = $(".dinner-series input[name='eb_id']").val();
            eb_client.event_list_attendees( {'id': eb_id}, function( response ){
                var attendees = response.attendees;
        //        $.each( attendees, function(index, attendee) {

         //       });
            });
        });
    });
});
