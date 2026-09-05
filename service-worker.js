// Configuration & État
let allArticles = [];
const newsContainer = document.getElementById('news-feed');
const searchInput = document.getElementById('search-input'); // À adapter selon ton ID
const categoryFilters = document.querySelectorAll('.filter-btn'); // À adapter

/**
 * Charge les news depuis le JSON généré
 */
async function fetchNews() {
    try {
        const response = await fetch('news.json');
        allArticles = await response.json();
        renderArticles(allArticles);
    } catch (error) {
        console.error("Erreur lors du chargement des dépêches:", error);
        newsContainer.innerHTML = "<p>Erreur de chargement des actualités.</p>";
    }
}

/**
 * Affiche les articles dans le DOM
 */
function renderArticles(articles) {
    const favorites = JSON.parse(localStorage.getItem('defense_pulse_favs') || '[]');
    
    newsContainer.innerHTML = articles.map(article => {
        const isFav = favorites.includes(article.link);
        const dateFormatted = new Date(article.date).toLocaleDateString('fr-FR', {
            day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
        });

        return `
            <article class="news-card" data-category="${article.category}">
                <div class="card-header">
                    <span class="source-badge">${article.source}</span>
                    <span class="date">${dateFormatted}</span>
                </div>
                <h3>${article.title}</h3>
                <p>${article.summary}</p>
                <div class="card-footer">
                    <a href="${article.link}" target="_blank" rel="noopener">Lire la suite</a>
                    <button onclick="toggleFavorite('${article.link}')" class="fav-btn ${isFav ? 'active' : ''}">
                        ${isFav ? '★' : '☆'}
                    </button>
                </div>
            </article>
        `;
    }).join('');
}

/**
 * Système de favoris
 */
window.toggleFavorite = (link) => {
    let favorites = JSON.parse(localStorage.getItem('defense_pulse_favs') || '[]');
    if (favorites.includes(link)) {
        favorites = favorites.filter(fav => fav !== link);
    } else {
        favorites.push(link);
    }
    localStorage.setItem('defense_pulse_favs', JSON.stringify(favorites));
    renderArticles(applyFilters()); // Rafraîchir l'affichage
};

/**
 * Filtrage et Recherche
 */
function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase();
    // Tu peux ajouter ici la logique de filtre par catégorie
    return allArticles.filter(article => {
        const matchesSearch = article.title.toLowerCase().includes(searchTerm) || 
                              article.summary.toLowerCase().includes(searchTerm);
        return matchesSearch;
    });
}

// Event Listeners
if(searchInput) {
    searchInput.addEventListener('input', () => {
        const filtered = applyFilters();
        renderArticles(filtered);
    });
}

// Initialisation
document.addEventListener('DOMContentLoaded', fetchNews);
