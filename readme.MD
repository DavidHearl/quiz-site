## Issues
- The results page needs to be styled when a user does not submit a value
- The round results shows all answers
- Make each user see the round results
- next logo does not save the score correctly
- David gets 0.5 points, maybe from the celebrity round

## Notes

When the user submits the form the database will update.
Poll the data with javascript then use the information to update the elements on the page.

- Keep the answers to the end of the round
- Keep the scores till the end of the round


    {% for player in players %}
        {% for point in player.points.item %}
            {{ point }}
        {% endfor %}
    {% endfor %}