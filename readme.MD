## Issues
- Which film is the oldest
- everyone sees everyones round results
- Timer from last entry
- Disable re entry in who is the imposter
- Rounding errors on the numbers movie release dates

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