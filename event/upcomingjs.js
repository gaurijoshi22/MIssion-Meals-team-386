document.addEventListener('DOMContentLoaded', function() {
    const eventList = document.getElementById('eventList');
    
    const events = [
        {
            name: 'Charity Gala Night',
            date: '2023-08-15',
            description: 'Join us for a glamorous night of fundraising and entertainment.'
        },
        {
            name: 'Community Food Drive',
            date: '2023-09-05',
            description: 'Help us collect food items for the less fortunate in our community.'
        },
        {
            name: 'Run for a Cause',
            date: '2023-09-20',
            description: 'Participate in a charity run to support children\'s education.'
        }
        // Add more event objects as needed
    ];
    
    events.forEach(event => {
        const eventCard = document.createElement('div');
        eventCard.classList.add('event-card');
        
        const eventName = document.createElement('div');
        eventName.classList.add('event-name');
        eventName.textContent = event.name;
        
        const eventDate = document.createElement('div');
        eventDate.classList.add('event-date');
        eventDate.textContent = new Date(event.date).toDateString();
        
        const eventDescription = document.createElement('div');
        eventDescription.classList.add('event-description');
        eventDescription.textContent = event.description;
        
        eventCard.appendChild(eventName);
        eventCard.appendChild(eventDate);
        eventCard.appendChild(eventDescription);
        
        eventList.appendChild(eventCard);
    });
});
