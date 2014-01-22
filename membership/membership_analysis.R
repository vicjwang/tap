  setwd('~/hacks/tap')
  
  
  mc.data = read.csv("mailchimp_members.csv", header=T)
  eb.data = read.csv("eventbrite_attendance.csv", header=T)
  
  data = merge(mc.data, eb.data, by.x = "Email.Address", by.y = "Email", all=T)
  
  emails = unique(data$Email)

  findAttendedEvents = function(email) {
    d = unique(eb.data[eb.data$Email == email, c("Event.Name", "Date.Attending")])
    d[order(as.Date(d[,2],format="%b %d, %Y")),]
  }
  
  formatDate = function(dateStr) {
    as.Date(dateStr, format="%b %d, %Y")
  }
  
  # make dictionary like structure mapping email -> list of events  
  eb.data$Email = as.character(eb.data$Email)
  eventMap = lapply(emails, findAttendedEvents)
  names(eventMap) = emails
  
  getMonthsAgoDateFrom = function(date, m) {
    date - 30.5*m
  }
  
  isEventInDateRange = function(eventDateStr, startDate, endDate) {
    eventDate = formatDate(eventDateStr)
    return (eventDate > startDate && eventDate < endDate) 
  }
  
  numberAttendedEventsInDateRange = function(email, startDate, endDate) {
    # for person, find all their events
    events = eventMap[[email]]
    if (is.null(events) | nrow(events) == 0 | length(events) == 0){
      return(0)
    }
    # for each event, see if it falls within date range. add to counter
    n = sum(sapply(events$Date.Attending, function(event) {
      isEventInDateRange(event, startDate, endDate)
    }))
    if (is.na(n)){
      return(0)
    }
    return(n)
  }

  # calculate "membership score" = 1 / R * e / E
  
  getDaysSinceLastEvent = function(email) {
    events = eventMap[[email]]
    if (is.null(events)) {
      return(1000)
    }
    days = as.integer(Sys.Date() - formatDate(tail(events$Date.Attending, n=1)))
    if (days < 0) {
      return(1)
    }
    days
  }
  
  getNumberEventsSinceFirstEvent = function(email) {
    events = eventMap[[email]]
    if (is.null(events)) {
      return(1000)
    }
    firstDate = formatDate(head(events$Date.Attending, n=1))
    events = unique(data[,c("Event.Name", "Date.Attending")])
    nrow(events[formatDate(events$Date.Attending) > firstDate,])
  }
  
  calcMembershipScore = function(email) {
    print(email)
    R = getDaysSinceLastEvent(email)
    print(R)
    e = nrow(eventMap[[email]])
    print(e)
    if ( e == 0 ) {
      return(0)
    }
    E = getNumberEventsSinceFirstEvent(email)
    print(E)
    1 / R * e / E
  }
  
  # TESTING
  quarterAgo = getMonthsAgoDateFrom( Sys.Date(), 3)
  halfYearAgo = getMonthsAgoDateFrom( Sys.Date(), 6)
  yearAgo = getMonthsAgoDateFrom( Sys.Date(), 12)
  today = Sys.Date()
  
  numberAttendedEventsInDateRange("vjwang45@gmail.com", quarterAgo, today)
  
  # part time members in last quarter
  eventsInLastQuarter = sapply(emails, function(email) {
    eventsInRange = numberAttendedEventsInDateRange(email, quarterAgo, today)
  })
  
  eventsInLastHalfYear = sapply(emails, function(email) {
    eventsInRange = numberAttendedEventsInDateRange(email, halfYearAgo, today)
  })
  
  eventsInLastYear = sapply(emails, function(email) {
    eventsInRange = numberAttendedEventsInDateRange(email, yearAgo, today)
  })
  
  
  members = data.frame(data$Email.Address, data$First.Name.x, data$Last.Name.x, eventsInLastQuarter, eventsInLastHalfYear, eventsInLastYear)
  um = unique(members[complete.cases(members),])
  
  write.csv(members, "member_types-jan14.csv", row.names=T, na="")
  write.csv(data, "tap_membership.csv", row.names=T, na="")
  
  t = 1
  
  peeps = um[um$eventsInLastYear >= t,"data.Email.Address"]
  
  scores = sapply(peeps, calcMembershipScore)
  
  # graph of how frequently our members attended events in last year
  par(mfrow=c(1,1))
  df = data.frame(emails, eventsInLastYear)
  table(df$eventsInLastYear)
  h = hist(df$eventsInLastYear, breaks=-1:30, main="Member Attendance in 2013", xlab = "# events attended", ylab="# members", labels=T)
  
  #graph of # events attended in last year vs mc member rating
  df = unique(data.frame(data$Email, data$MEMBER_RATING))
  df$data.MEMBER_RATING[is.na(df$data.MEMBER_RATING)] = 0 # replace NAs with 0 aka doesn't get our newsletter
  df = data.frame(df, n=eventsInLastYear)
  plot(df$data.MEMBER_RATING, eventsInLastYear)
  par(mfrow=c(3,2))
  
  hist(df[df$data.MEMBER_RATING==5,]$n, breaks = -1:30, labels=T, xlab="# events attended", ylab="# members", main="Attendance of Newsletter High Activity in 2013") # rating = 5
  hist(df[df$data.MEMBER_RATING==4,]$n, breaks = -1:30, labels=T, xlab="# events attended", ylab="# members", main="Attendance of Newsletter Some Activity in 2013") # rating = 5
  hist(df[df$data.MEMBER_RATING==3,]$n, breaks = -1:30, labels=T, xlab="# events attended", ylab="# members", main="Attendance of Newsletter Limited Activity in 2013") # rating = 5
  hist(df[df$data.MEMBER_RATING==2,]$n, breaks = -1:30, labels=T, xlab="# events attended", ylab="# members", main="Attendance of Newsletter No Activity in 2013") # rating = 5
  hist(df[df$data.MEMBER_RATING==1,]$n, breaks = -1:30, labels=T, xlab="# events attended", ylab="# members", main="Attendance of Newsletter Resubscriber in 2013") # rating = 5
  hist(df[df$data.MEMBER_RATING==0,]$n, breaks = -1:30, labels=T, xlab="# events attended", ylab="# members", main="Attendance of Non-Newsletter Recipients in 2013") # rating = 5
  
  
  # volunteers. get names of those who expressed interest in volunteering
  volCols = c(59,77,79) #grep("volun", cols) #11  59  77  79 117
  volunteers = unique(unlist(lapply(volCols, function(c) {
    data[complete.cases(data[,c]) & data[,c] != "",1]
  })))
  volunteers2 = unique(unlist(data[complete.cases(data[,117]) & data[,117] == "Yes","Email.Address"]))
  volunteers = unique(tolower(unlist(c(list(volunteers), list(volunteers2)))))
  write.csv(volunteers, "volunteers_2013.csv", row.names=FALSE, col.names=FALSE, quote=F)
  
  checkVolunteer = function(email) {
    data[data$Email==email, c(volCols,117)]
  }
  
  # most popular first event
  firstEvents = table(mc.data[,"firstevent"])
  par(las=2)
  par(mar=c(5,25,1,1))
  barplot(firstEvents, main="First Events", xlab="# People", names.arg=names(firstEvents), horiz=T, axisnames=T)
  
  # check if no for newsletter
  summary(eb.data[eb.data[,19]=="Please check if no",1])
  
  totalAttended = function(eventName) {
    nrow(eb.data[eb.data[,1]==eventName,])
  }
  
  totalDeclined = function(eventName) {
    length(eb.data[eb.data[,19]=="Please check if no" & eb.data[,1]==eventName,1])
  }
  # TODO bar graph, xaxis = event, yaxis=#people, % unsubscibed
  t = 25
  eventNames = names(summary(eb.data[eb.data[,19]=="Please check if no",1]))[1:t] #unique(eb.data[,1])
  decliners = sapply( eventNames, function(eventName) {
    totalDeclined(eventName)/totalAttended(eventName)
  })
  barplot(decliners, main="Percentage Declined Newsletter on EventBrite", xlab="% declined", names.arg=eventNames, horiz=T, axisnames=T)
    
  # industry TODO piechart
  industryCols = grep("industry", names(data))
  s = summary(mc.data[mc.data[,9]!="",9])
  length(mc.data[mc.data[,9]!="",9])
  lbls = paste(names(s),s,sep=" ")
  pie(s, labels=lbls, main="Industry breakdown (868 reponses)")
  
  # DEMO
  df[df$eventsInLastYear ==5, ]
  eventMap[['jamtonium@gmail.com']]
  