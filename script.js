// Remove this line
// const accessToken = 'YOUR_SPOTIFY_ACCESS_TOKEN';

// Remove this line
// const spotifyApiEndpoint = 'https://api.spotify.com/v1';

// Update the OK Button event listener
document.getElementById('okButton').addEventListener('click', async function() {
    if (selectedGenres.length > 0) {
        document.getElementById('genresPage').style.display = 'none';
        document.getElementById('artistsPage').style.display = 'block';

        const artistContainer = document.getElementById('artistContainer');
        artistContainer.innerHTML = '';

        try {
            const artists = await apiRequest('/artists', 'POST', { genres: selectedGenres });

            artists.forEach(artist => {
                const artistBox = document.createElement('div');
                artistBox.classList.add('artist-box');
                artistBox.textContent = artist.name;
                artistBox.dataset.artist = artist.id;
                artistContainer.appendChild(artistBox);
            });
        } catch (error) {
            console.error('Error fetching artists:', error);
        }
    } else {
        alert('Please select at least one genre.');
    }
});

// Update the Finish Button event listener
document.getElementById('finishButton').addEventListener('click', async function() {
    if (selectedArtists.length > 0) {
        document.getElementById('artistsPage').style.display = 'none';
        document.getElementById('recommendationsPage').style.display = 'block';

        const recommendationsContainer = document.getElementById('recommendationsContainer');
        recommendationsContainer.innerHTML = '';

        try {
            const data = await apiRequest('/recommendations', 'POST', { artists: selectedArtists });

            data.tracks.forEach(track => {
                const recommendationBox = document.createElement('div');
                recommendationBox.classList.add('card');
                recommendationBox.textContent = `Song recommendation: ${track.name} by ${track.artists[0].name}`;
                recommendationsContainer.appendChild(recommendationBox);
            });
        } catch (error) {
            console.error('Error fetching recommendations:', error);
        }
    } else {
        alert('Please select at least one artist.');
    }
});