document.addEventListener("DOMContentLoaded", () => {
    console.log("📈 CryptoKitty Loaded");

    const coinButtons = document.querySelectorAll("#coin-list button");
    const updateButton = document.getElementById("update-prices-btn");
    const selectedCoinsElement = document.getElementById("selected-coins");

    // Toggle active state on button click
    coinButtons.forEach(button => {
        button.addEventListener("click", () => {
            button.classList.toggle("active");
        });
    });

    // Update Prices Button Logic
    updateButton.addEventListener("click", () => {
        const selectedCoins = Array.from(coinButtons)
            .filter(button => button.classList.contains("active"))
            .map(button => button.value);

        if (selectedCoins.length === 0) {
            alert("Please select at least one coin.");
            return;
        }

        fetch('/prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coins: selectedCoins })
        })
        .then(response => response.json())
        .then(data => {
            console.log("💰 Prices Data:", data);
            selectedCoinsElement.innerHTML = '';
            selectedCoins.forEach(coin => {
                const coinData = data.prices[coin];
                if (!coinData) return;

                const coinElement = document.createElement('li');
                coinElement.textContent = `${coin}: $${coinData.price} (${coinData.change}%)`;
                coinElement.style.color = coinData.change < 0 ? 'red' : 'green';
                selectedCoinsElement.appendChild(coinElement);
            });
        })
        .catch(error => console.error('Error fetching prices:', error));
    });
});
