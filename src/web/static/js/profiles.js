// Profiles Management
class ProfilesManager {
    constructor() {
        this.profiles = [];
        this.filteredProfiles = [];
        this.currentFilter = 'all';
        this.currentSort = 'created_desc';
        this.searchTerm = '';
    }

    render(profiles = []) {
        this.profiles = profiles;
        this.applyFiltersAndSort();
        this.updateStats();
        this.renderProfiles();
    }

    applyFiltersAndSort() {
        let filtered = [...this.profiles];

        // Apply search filter
        if (this.searchTerm) {
            filtered = filtered.filter(profile => 
                profile.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                profile.location.city?.toLowerCase().includes(this.searchTerm.toLowerCase())
            );
        }

        // Apply status filter
        switch (this.currentFilter) {
            case 'active':
                filtered = filtered.filter(p => p.is_active);
                break;
            case 'inactive':
                filtered = filtered.filter(p => !p.is_active);
                break;
        }

        // Apply sorting
        switch (this.currentSort) {
            case 'created_desc':
                filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                break;
            case 'created_asc':
                filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
                break;
            case 'name_asc':
                filtered.sort((a, b) => a.name.localeCompare(b.name));
                break;
            case 'name_desc':
                filtered.sort((a, b) => b.name.localeCompare(a.name));
                break;
            case 'active_first':
                filtered.sort((a, b) => b.is_active - a.is_active);
                break;
        }

        this.filteredProfiles = filtered;
    }

    updateStats() {
        const totalProfiles = this.profiles.length;
        const activeProfiles = this.profiles.filter(p => p.is_active).length;
        const matchesToday = this.profiles.filter(p => 
            p.last_match && new Date(p.last_match).toDateString() === new Date().toDateString()
        ).length;

        Utils.updateElement('total-profiles-count', totalProfiles);
        Utils.updateElement('active-profiles-count', activeProfiles);
        Utils.updateElement('matches-today', matchesToday);
        Utils.updateElement('notifications-pending', '0'); // Would come from API
    }

    renderProfiles() {
        const container = document.getElementById('profiles-list');
        const emptyState = document.getElementById('profiles-empty');
        
        if (!container) return;

        if (this.filteredProfiles.length === 0) {
            container.style.display = 'none';
            if (emptyState) {
                emptyState.style.display = 'block';
            }
            return;
        }

        container.style.display = 'flex';
        if (emptyState) {
            emptyState.style.display = 'none';
        }

        container.innerHTML = this.filteredProfiles.map(profile => this.renderProfileCard(profile)).join('');
    }

    renderProfileCard(profile) {
        const neighborhoods = profile.location.neighborhoods || [];
        const propertyTypes = profile.property_types || [];
        
        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100 property-card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">${Utils.escapeHtml(profile.name)}</h6>
                        <span class="badge bg-${profile.is_active ? 'success' : 'secondary'}">
                            ${profile.is_active ? 'פעיל' : 'לא פעיל'}
                        </span>
                    </div>
                    <div class="card-body">
                        <div class="mb-2">
                            <small class="text-muted">מחיר:</small><br>
                            <span>${this.formatPriceRange(profile.price_range)}</span>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted">חדרים:</small><br>
                            <span>${this.formatRoomsRange(profile.rooms_range)}</span>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted">עיר:</small><br>
                            <span>${profile.location.city || 'לא צוין'}</span>
                        </div>
                        ${neighborhoods.length > 0 ? `
                            <div class="mb-2">
                                <small class="text-muted">שכונות:</small><br>
                                <div class="mt-1">
                                    ${neighborhoods.map(n => `<span class="badge bg-light text-dark me-1">${Utils.escapeHtml(n)}</span>`).join('')}
                                </div>
                            </div>
                        ` : ''}
                        ${propertyTypes.length > 0 ? `
                            <div class="mb-2">
                                <small class="text-muted">סוגי נכסים:</small><br>
                                <div class="mt-1">
                                    ${propertyTypes.map(t => `<span class="badge bg-info text-white me-1">${Utils.escapeHtml(t)}</span>`).join('')}
                                </div>
                            </div>
                        ` : ''}
                        <div class="mb-3">
                            <small class="text-muted">נוצר:</small><br>
                            <span>${Utils.formatDate(profile.created_at)}</span>
                        </div>
                        <div class="mb-3">
                            <small class="text-muted">התאמה אחרונה:</small><br>
                            <span>${profile.last_match ? Utils.formatDate(profile.last_match) : 'אין'}</span>
                        </div>
                    </div>
                    <div class="card-footer">
                        <div class="btn-group w-100">
                            <button class="btn btn-outline-primary btn-sm" onclick="ProfilesManager.edit('${profile.id}')">
                                <i class="fas fa-edit"></i> ערוך
                            </button>
                            <button class="btn btn-outline-${profile.is_active ? 'warning' : 'success'} btn-sm" 
                                    onclick="ProfilesManager.toggle('${profile.id}')">
                                <i class="fas fa-${profile.is_active ? 'pause' : 'play'}"></i>
                                ${profile.is_active ? 'השבת' : 'הפעל'}
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="ProfilesManager.delete('${profile.id}')">
                                <i class="fas fa-trash"></i> מחק
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    formatPriceRange(range) {
        const min = range.min ? Utils.formatNumber(range.min) + '₪' : 'ללא מינימום';
        const max = range.max ? Utils.formatNumber(range.max) + '₪' : 'ללא מקסימום';
        return `${min} - ${max}`;
    }

    formatRoomsRange(range) {
        const min = range.min || 'ללא מינימום';
        const max = range.max || 'ללא מקסימום';
        return `${min} - ${max}`;
    }

    // Event handlers
    filter(filterType) {
        this.currentFilter = filterType;
        this.applyFiltersAndSort();
        this.renderProfiles();
    }

    search(term) {
        this.searchTerm = term;
        this.applyFiltersAndSort();
        this.renderProfiles();
    }

    sort(sortType) {
        this.currentSort = sortType;
        this.applyFiltersAndSort();
        this.renderProfiles();
    }

    async add() {
        this.showProfileModal();
    }

    async edit(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;

        this.showProfileModal(profile);
    }

    async toggle(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;

        try {
            await API.put(`/profiles/${profileId}`, { is_active: !profile.is_active });
            Utils.showAlert(`הפרופיל ${profile.is_active ? 'הושבת' : 'הופעל'} בהצלחה`, 'success');
            
            // Update local state
            profile.is_active = !profile.is_active;
            this.render(this.profiles);
            
        } catch (error) {
            Utils.showAlert('שגיאה בעדכון הפרופיל', 'danger');
        }
    }

    async delete(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;

        const confirmed = await Utils.confirm(`האם אתה בטוח שברצונך למחוק את הפרופיל "${profile.name}"?`);
        if (!confirmed) return;

        try {
            await API.delete(`/profiles/${profileId}`);
            Utils.showAlert('הפרופיל נמחק בהצלחה', 'success');
            
            // Remove from local state
            this.profiles = this.profiles.filter(p => p.id !== profileId);
            this.render(this.profiles);
            
        } catch (error) {
            Utils.showAlert('שגיאה במחיקת הפרופיל', 'danger');
        }
    }

    showProfileModal(profile = null) {
        const modal = document.getElementById('profileModal');
        if (!modal) return;

        const title = document.getElementById('profileModalTitle');
        const form = document.getElementById('profileForm');
        
        if (profile) {
            title.textContent = 'ערוך פרופיל חיפוש';
            this.populateProfileForm(profile);
        } else {
            title.textContent = 'הוסף פרופיל חיפוש חדש';
            form.reset();
            document.getElementById('profileId').value = '';
        }

        new bootstrap.Modal(modal).show();
    }

    populateProfileForm(profile) {
        document.getElementById('profileId').value = profile.id;
        document.getElementById('profileName').value = profile.name;
        document.getElementById('minPrice').value = profile.price_range.min || '';
        document.getElementById('maxPrice').value = profile.price_range.max || '';
        document.getElementById('minRooms').value = profile.rooms_range.min || '';
        document.getElementById('maxRooms').value = profile.rooms_range.max || '';
        document.getElementById('city').value = profile.location.city || '';
        document.getElementById('neighborhoods').value = profile.location.neighborhoods ? profile.location.neighborhoods.join(', ') : '';
        document.getElementById('isActive').checked = profile.is_active;

        // Set property types
        document.querySelectorAll('input[type="checkbox"][value]').forEach(checkbox => {
            checkbox.checked = profile.property_types.includes(checkbox.value);
        });
    }

    async saveProfile() {
        const form = document.getElementById('profileForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const profileId = document.getElementById('profileId').value;
        const propertyTypes = Array.from(document.querySelectorAll('input[type="checkbox"][value]:checked'))
            .map(cb => cb.value);

        const profileData = {
            name: document.getElementById('profileName').value,
            price_range: {
                min: parseInt(document.getElementById('minPrice').value) || null,
                max: parseInt(document.getElementById('maxPrice').value) || null
            },
            rooms_range: {
                min: parseFloat(document.getElementById('minRooms').value) || null,
                max: parseFloat(document.getElementById('maxRooms').value) || null
            },
            location: {
                city: document.getElementById('city').value,
                neighborhoods: document.getElementById('neighborhoods').value.split(',').map(s => s.trim()).filter(s => s)
            },
            property_types: propertyTypes,
            is_active: document.getElementById('isActive').checked
        };

        try {
            let response;
            if (profileId) {
                response = await API.put(`/profiles/${profileId}`, profileData);
                Utils.showAlert('הפרופיל עודכן בהצלחה', 'success');
            } else {
                response = await API.post('/profiles', profileData);
                Utils.showAlert('הפרופיל נוצר בהצלחה', 'success');
            }

            bootstrap.Modal.getInstance(document.getElementById('profileModal')).hide();
            
            // Reload profiles
            const profilesResponse = await API.get('/profiles');
            this.render(profilesResponse.profiles || []);

        } catch (error) {
            Utils.showAlert('שגיאה בשמירת הפרופיל', 'danger');
        }
    }

    async exportProfiles() {
        try {
            const data = {
                export_date: new Date().toISOString(),
                profiles: this.profiles
            };
            
            const jsonData = JSON.stringify(data, null, 2);
            const filename = `profiles_export_${new Date().toISOString().split('T')[0]}.json`;
            
            Utils.downloadFile(jsonData, filename);
            Utils.showAlert('הפרופילים יוצאו בהצלחה', 'success');
            
        } catch (error) {
            Utils.showAlert('שגיאה בייצוא הפרופילים', 'danger');
        }
    }
}

// Create global instance
window.ProfilesManager = new ProfilesManager();

// Global functions for the UI
window.showAddProfileModal = () => ProfilesManager.add();
window.saveProfile = () => ProfilesManager.saveProfile();
window.exportProfiles = () => ProfilesManager.exportProfiles();
window.filterProfiles = () => {
    const filter = document.getElementById('profile-filter').value;
    ProfilesManager.filter(filter);
};
window.searchProfiles = () => {
    const term = document.getElementById('profile-search').value;
    ProfilesManager.search(term);
};
window.sortProfiles = () => {
    const sort = document.getElementById('profile-sort').value;
    ProfilesManager.sort(sort);
};
