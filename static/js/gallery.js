/**
 * Gallery Module
 * Handles image gallery interactions, preview modal, filtering, and infinite scroll
 */

(function() {
    'use strict';

    // ============================================
    // STATE
    // ============================================
    const state = {
        currentPage: 1,
        isLoading: false,
        hasMore: true,
        currentFilter: '*',
        currentView: 'masonry',
        previewImages: [],
        previewIndex: 0,
        previewData: [],
    };

    // ============================================
    // DOM REFS
    // ============================================
    const grid = document.getElementById('photoGrid');
    const skeleton = document.getElementById('skeletonGrid');
    const sentinel = document.getElementById('sentinel');
    const loadMoreIndicator = document.getElementById('loadMoreIndicator');
    const endOfContent = document.getElementById('endOfContent');
    const filterList = document.getElementById('filterList');
    const viewBtns = document.querySelectorAll('.view-toggle-btn');

    // Preview
    const previewModal = document.getElementById('previewModal');
    const previewOverlay = document.getElementById('previewOverlay');
    const previewClose = document.getElementById('previewClose');
    const previewImage = document.getElementById('previewImage');
    const previewTitle = document.getElementById('previewTitle');
    const previewCounter = document.getElementById('previewCounter');
    const previewPrev = document.getElementById('previewPrev');
    const previewNext = document.getElementById('previewNext');
    const previewDownload = document.getElementById('previewDownload');
    const previewLoader = document.querySelector('.preview-loader');

    // ============================================
    // COLLECT ALL PREVIEW IMAGES
    // ============================================
    function collectPreviewImages() {
        state.previewData = [];
        document.querySelectorAll('.preview-btn').forEach((btn, index) => {
            const img = btn.dataset.image;
            const title = btn.dataset.title || 'Photo';
            const fullImage = btn.dataset.fullImage || img;
            state.previewData.push({
                url: img,
                fullUrl: fullImage,
                title: title,
                btn: btn
            });
        });
        state.previewImages = state.previewData.map(d => d.url);
    }

    // ============================================
    // PREVIEW MODAL
    // ============================================
    let previewImageCache = {};
    let currentPreviewUrl = '';

    function openPreview(url, title, index) {
        // Find the actual data
        let dataIndex = index;
        if (dataIndex === undefined || dataIndex === null) {
            dataIndex = state.previewData.findIndex(d => d.url === url);
        }
        if (dataIndex === -1) dataIndex = 0;
        
        state.previewIndex = dataIndex;
        const data = state.previewData[dataIndex];
        if (!data) return;

        const thumbUrl = data.url;
        const fullUrl = data.fullUrl || thumbUrl;
        currentPreviewUrl = fullUrl;
        previewTitle.textContent = data.title || title || 'Photo';
        updatePreviewCounter();

        // Reset
        previewImage.classList.remove('loaded');
        previewLoader.classList.remove('hidden');
        previewImage.onload = function () {
            previewLoader.classList.add('hidden');
            previewImage.classList.add('loaded');
        };
        previewImage.onerror = function () {
            previewLoader.classList.add('hidden');
        };

        // Prefer the full image when available so preview opens large; fall back to thumbnail
        if (fullUrl && fullUrl !== thumbUrl) {
            previewImage.src = fullUrl;
        } else if (thumbUrl) {
            previewImage.src = thumbUrl;
        } else {
            previewImage.src = '';
        }

        updateNavButtons();

        if (fullUrl && fullUrl !== thumbUrl) {
            if (previewImageCache[fullUrl]) {
                showPreviewImage(previewImageCache[fullUrl]);
            } else {
                const img = new Image();
                img.crossOrigin = 'anonymous';
                img.onload = function() {
                    previewImageCache[fullUrl] = this;
                    showPreviewImage(this);
                };
                img.onerror = function() {
                    // keep the thumbnail if high-res load fails
                };
                img.src = fullUrl;
            }
        }

        // Show modal
        previewModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        document.body.style.position = 'fixed';
        document.body.style.width = '100%';
    }

    function showPreviewImage(img) {
        previewImage.src = img.src;
        previewImage.onload = function() {
            previewLoader.classList.add('hidden');
            previewImage.classList.add('loaded');
        };
        if (img.complete) {
            previewLoader.classList.add('hidden');
            previewImage.classList.add('loaded');
        }
    }

    function updatePreviewCounter() {
        const total = state.previewData.length;
        const current = state.previewIndex + 1;
        previewCounter.textContent = total > 0 ? `${current} / ${total}` : '1 / 1';
    }

    function updateNavButtons() {
        const total = state.previewData.length;
        previewPrev.disabled = state.previewIndex <= 0 || total <= 1;
        previewNext.disabled = state.previewIndex >= total - 1 || total <= 1;
    }

    function navigatePreview(direction) {
        const total = state.previewData.length;
        if (total === 0) return;
        
        let newIndex = state.previewIndex + direction;
        if (newIndex < 0) newIndex = 0;
        if (newIndex >= total) newIndex = total - 1;
        
        if (newIndex !== state.previewIndex) {
            const data = state.previewData[newIndex];
            if (data) {
                openPreview(data.url, data.title, newIndex);
            }
        }
    }

    function closePreview() {
        previewModal.classList.remove('active');
        document.body.style.overflow = '';
        document.body.style.position = '';
        document.body.style.width = '';
    }

    // Preview event listeners
    if (previewOverlay) {
        previewOverlay.addEventListener('click', closePreview);
    }
    if (previewClose) {
        previewClose.addEventListener('click', closePreview);
    }

    if (previewPrev) {
        previewPrev.addEventListener('click', (e) => {
            e.stopPropagation();
            navigatePreview(-1);
        });
    }

    if (previewNext) {
        previewNext.addEventListener('click', (e) => {
            e.stopPropagation();
            navigatePreview(1);
        });
    }

    // Keyboard shortcuts for preview
    document.addEventListener('keydown', (e) => {
        if (!previewModal.classList.contains('active')) {
            return;
        }
        if (e.key === 'Escape') closePreview();
        if (e.key === 'ArrowLeft') navigatePreview(-1);
        if (e.key === 'ArrowRight') navigatePreview(1);
    });

    // Touch swipe support for preview
    let touchStartX = 0;
    let touchEndX = 0;
    const previewContainer = document.querySelector('.preview-image-container');
    
    if (previewContainer) {
        previewContainer.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        previewContainer.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });
    }

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                navigatePreview(1);
            } else {
                navigatePreview(-1);
            }
        }
    }

    // ============================================
    // INTERSECTION OBSERVER - INFINITE SCROLL
    // ============================================
    let observer = null;

    function setupIntersectionObserver() {
        if (observer) observer.disconnect();
        
        observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !state.isLoading && state.hasMore) {
                    loadMore();
                }
            });
        }, {
            rootMargin: '200px',
            threshold: 0.1,
        });

        if (sentinel) observer.observe(sentinel);
    }

    // ============================================
    // SKELETON HELPERS
    // ============================================
    function showSkeleton() {
        if (skeleton) {
            skeleton.style.display = 'grid';
        }
    }

    function hideSkeleton() {
        if (skeleton) {
            skeleton.style.display = 'none';
        }
    }

    // ============================================
    // TOAST NOTIFICATIONS
    // ============================================
    function showToast(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            error: 'fa-exclamation-circle',
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        const icon = icons[type] || icons.info;
        toast.innerHTML = `
            <i class="fa ${icon} toast-icon"></i>
            <div class="toast-content">${message}</div>
            <button class="toast-close" aria-label="Close">
                <i class="fa fa-times"></i>
            </button>
        `;

        container.appendChild(toast);

        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                toast.classList.add('remove');
                setTimeout(() => toast.remove(), 300);
            });
        }

        if (duration > 0) {
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.classList.add('remove');
                    setTimeout(() => toast.remove(), 300);
                }
            }, duration);
        }

        return toast;
    }

    // ============================================
    // LOAD MORE
    // ============================================
    function loadMore() {
        if (state.isLoading || !state.hasMore) return;
        state.isLoading = true;
        if (loadMoreIndicator) loadMoreIndicator.style.display = 'flex';

        const currentPage = state.currentPage;
        const filter = state.currentFilter;
        const search = '';

        fetch(`/api/photos/?page=${currentPage + 1}&filter=${filter}&search=${encodeURIComponent(search)}`)
            .then(res => {
                if (!res.ok) {
                    throw new Error(`Server error: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.error) {
                    showToast(data.error, 'error');
                    state.hasMore = false;
                } else if (data.photos && data.photos.length > 0) {
                    appendPhotos(data.photos);
                    state.currentPage = currentPage + 1;
                    state.hasMore = data.has_more;
                    collectPreviewImages();
                    updatePagination(data);
                } else {
                    state.hasMore = false;
                }
            })
            .catch(err => {
                console.error('Gallery load error:', err);
                showToast('Failed to load photos. Please try again.', 'error');
                state.hasMore = false;
            })
            .finally(() => {
                state.isLoading = false;
                if (loadMoreIndicator) loadMoreIndicator.style.display = 'none';
                hideSkeleton();
                if (!state.hasMore && endOfContent) {
                    endOfContent.style.display = 'block';
                }
            });
    }

    function appendPhotos(photos) {
        const fragment = document.createDocumentFragment();
        photos.forEach((photo, index) => {
            // Skip duplicates by photo id if already rendered
            if (grid && grid.querySelector(`[data-id=\"${photo.id}\"]`)) return;
            const card = createPhotoCard(photo, index);
            fragment.appendChild(card);
        });
        if (grid) grid.appendChild(fragment);
        hideSkeleton();
        updateCounts();
    }

    function createPhotoCard(photo, index) {
        const card = document.createElement('div');
        card.className = `photo-card ${photo.category || ''}`;
        card.dataset.id = photo.id;
        card.dataset.category = photo.category || '';

        const currentIndex = (grid ? grid.children.length : 0) + index;

        card.innerHTML = `
            <div class="photo-card-inner">
                <img class="photo-img" 
                     src="${photo.thumb || photo.url}" 
                     alt="${photo.title || 'Photo'}"
                     loading="lazy"
                     decoding="async"
                     fetchpriority="low">
                <div class="photo-card-overlay">
                    <div class="photo-meta">
                        <span class="photo-category">${photo.category || 'Photo'}</span>
                        <span class="photo-date">${photo.date || 'Today'}</span>
                    </div>
                    <div class="photo-actions-overlay">
                        <button class="photo-action-btn preview-btn" 
                                data-image="${photo.url}"
                                data-title="${photo.title || 'Photo'}"
                                data-index="${currentIndex}">
                            <i class="fa fa-expand"></i>
                        </button>
                        <button class="photo-action-btn like-btn" data-id="${photo.id}">
                            <i class="fa fa-heart-o"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Add preview click
        const previewBtn = card.querySelector('.preview-btn');
        if (previewBtn) {
            previewBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const url = previewBtn.dataset.image;
                const title = previewBtn.dataset.title || 'Photo';
                const idx = parseInt(previewBtn.dataset.index) || 0;
                openPreview(url, title, idx);
            });
        }

        // Add like
        const likeBtn = card.querySelector('.like-btn');
        if (likeBtn) {
            likeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                likeBtn.classList.toggle('liked');
            });
        }

        // Click card to open preview
        card.addEventListener('click', () => {
            const img = card.querySelector('.photo-img');
            const title = img ? img.alt : 'Photo';
            const url = img ? img.src : '';
            const idx = parseInt(card.dataset.index) || 0;
            if (url) openPreview(url, title, idx);
        });

        return card;
    }

    // ============================================
    // FILTER
    // ============================================
    if (filterList) {
        filterList.addEventListener('click', (e) => {
            const item = e.target.closest('.filter-item');
            if (!item) return;

            filterList.querySelectorAll('.filter-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');

            // Normalize filter value: strip leading '.' used for CSS classes
            let filterVal = item.dataset.filter || '*';
            if (filterVal.startsWith('.')) filterVal = filterVal.slice(1);
            state.currentFilter = filterVal;
            state.currentPage = 0;
            state.hasMore = true;
            state.isLoading = false;

            // Reset grid
            if (grid) grid.innerHTML = '';
            showSkeleton();
            if (endOfContent) endOfContent.style.display = 'none';

            // Force clean preview state
            if (previewModal) previewModal.classList.remove('active');

            // Reload
            loadMore();
        });
    }

    // ============================================
    // VIEW TOGGLE
    // ============================================
    viewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            viewBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const view = btn.dataset.view;
            state.currentView = view;

            if (grid) {
                grid.classList.remove('masonry', 'grid');
                grid.classList.add(view);
            }
        });
    });

    // ============================================
    // PHOTO COUNT
    // ============================================
    function updateCounts() {
        const count = grid ? grid.querySelectorAll('.photo-card').length : 0;
        const photoCountEl = document.getElementById('photoCount');
        const albumCountEl = document.getElementById('albumCount');
        if (photoCountEl) photoCountEl.textContent = count;
        if (albumCountEl) albumCountEl.textContent = Math.ceil(count / 20) || 0;
    }

    // ============================================
    // UPDATE PAGINATION
    // ============================================
    function updatePagination(data) {
        const currentPageEl = document.getElementById('currentPage');
        const totalPagesEl = document.getElementById('totalPages');
        if (currentPageEl) currentPageEl.textContent = data.current_page || 1;
        if (totalPagesEl) totalPagesEl.textContent = data.total_pages || 1;
    }

    // ============================================
    // DOWNLOAD BUTTON
    // ============================================
    if (previewDownload) {
        previewDownload.addEventListener('click', () => {
            const data = state.previewData[state.previewIndex];
            if (!data) return;
            
            const url = data.fullUrl || data.url;
            const title = data.title || 'photo';
            
            // Create download link
            const link = document.createElement('a');
            link.href = url;
            link.download = `${title}.jpg`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    // Also handle download buttons in cards
    document.querySelectorAll('.download-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const url = btn.href;
            if (url) {
                const link = document.createElement('a');
                link.href = url;
                link.download = 'photo.jpg';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        });
    });

    // ============================================
    // INIT
    // ============================================
    function init() {
        // Hide skeleton after initial load
        if (skeleton) {
            setTimeout(() => {
                skeleton.style.display = 'none';
            }, 500);
        }

        setupIntersectionObserver();
        updateCounts();
        collectPreviewImages();

        // Preview buttons on existing cards
        document.querySelectorAll('.preview-btn').forEach((btn, index) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const url = btn.dataset.image;
                const title = btn.dataset.title || 'Photo';
                const idx = btn.dataset.index !== undefined ? parseInt(btn.dataset.index) : index;
                openPreview(url, title, idx);
            });
        });

        // Card clicks
        document.querySelectorAll('.photo-card').forEach((card, index) => {
            card.addEventListener('click', () => {
                const img = card.querySelector('.photo-img');
                const title = img ? img.alt : 'Photo';
                const url = img ? img.src : '';
                if (url) openPreview(url, title, index);
            });
        });

        // Like buttons
        document.querySelectorAll('.like-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                btn.classList.toggle('liked');
            });
        });
    }

    // ============================================
    // DOM READY
    // ============================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
