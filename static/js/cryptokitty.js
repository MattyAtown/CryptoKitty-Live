document.addEventListener("DOMContentLoaded", () => {
    console.log("📈 CryptoKitty Loaded");

    const cryptoChart = new Chart(document.getElementById('crypto-graph').getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Time' } },
                y: { title: { display: true, text: 'Price (USD)' }, min: -20, max: 20 }
            }
        }
    });

    function updateSelectedCoins() {
        const selectedCoins = [];
        document.querySelectorAll('#coin-list input[type="checkbox"]:checked').forEach(checkbox => {
            selectedCoins.push(checkbox.value);
        });

        if (selectedCoins.length === 0) return;

        fetch('/prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coins: selectedCoins })
        })
        .then(response => response.json())
        .then(data => console.log("💰 Prices Data:", data))
        .catch(error => console.error('Error fetching prices:', error));
    }

    document.getElementById('update-prices-btn').addEventListener('click', updateSelectedCoins);
});
