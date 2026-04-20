# Newsletter "Stay Updated" Fix - Progress Tracker
Current: e:/login | Target: Fix newsletter signup on main_home (backend/accounts/)

## Plan Status: ✅ APPROVED

### 📋 Steps to Complete:

#### 1. **Add Newsletter Model** ✅
   - File: `backend/accounts/models.py`
   - Add Newsletter model (email, subscribed_at, is_active, ip_address)

#### 2. **Create Newsletter View** ✅
   - File: `backend/accounts/views.py`
   - Add `@csrf_exempt` `newsletter_subscribe` view (validate, save, send confirmation)

#### 3. **Add Newsletter URL** ✅
   - File: `backend/accounts/urls.py`
   - Add `path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe')`

#### 4. **Update Footer Form** [ ]
   - File: `backend/accounts/templates/components/footer.html`
   - Replace JS `handleNewsletterSignup` with AJAX to `/accounts/newsletter/subscribe/`
   - Add loading/error states

#### 5. **Run Migrations** ✅
   ```
   cd backend
   python manage.py makemigrations accounts
   python manage.py migrate
   ```
   Status: Migrations created and applied
   ```
   cd backend
   python manage.py makemigrations accounts
   python manage.py migrate
   ```

#### 6. **Test End-to-End** [ ]
   - Visit /main_home/
   - Submit newsletter form
   - Check: DB entry, confirmation email sent, no duplicates

#### 7. **Restart Server** [ ]
   ```
   cd backend
   python manage.py runserver
   ```

---

## Current Step: 1/7 - Adding Newsletter Model

**Next Action**: Edit `backend/accounts/models.py`

