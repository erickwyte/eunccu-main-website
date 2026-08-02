from pathlib import Path

root = Path('c:/Users/stewa/Downloads/System/System/website/templates/website')
files = {
    'contact.html': """{% extends 'website/base.html' %}
{% load static %}

{% block title %}Contact Us | EUNCCU{% endblock %}

{% block content %}
<div class=\"header-height\"></div>

<div class=\"pager-header\">
    <div class=\"container\">
        <div class=\"page-content\">
            <h2>Contact Us</h2>
            <p>Do You Have a Question, Inquiry or Comment? Then Get in touch with us !</p>
            <ol class=\"breadcrumb\">
                <li class=\"breadcrumb-item\"><a href=\"{% url 'website:home' %}\">Home</a></li>
                <li class=\"breadcrumb-item active\">Contact</li>
            </ol>
        </div>
    </div>
</div><!-- /Page Header -->

<section class=\"contact-section padding\">
    <iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d249.35858427533262!2d35.93165600603046!3d-0.365030430931147!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x18298752c9fed347%3A0xfcf061f5ffb07c68!2sEgerton%20B1%20Church!5e0!3m2!1sen!2ske!4v1723058489533!5m2!1sen!2ske\"
        width=\"100%\" height=\"450\" style=\"border:0px solid #000000;\" allowfullscreen=\"\" loading=\"lazy\"
        referrerpolicy=\"no-referrer-when-downgrade\"></iframe>
    <div class=\"container\">
        <div class=\"row contact-wrap\">
            <div class=\"col-md-6 xs-padding\">
                <div class=\"contact-info\">
                    <h3>Get in touch</h3>
                    <p>We’re here to assist you with any questions or inquiries you may have. Feel free to reach out to us for more information about our services, suggestions, or assistance.</p>
                    <ul>
                        <li><i class=\"ti-location-pin\"></i> Egerton University, Njoro, Nakuru-Kenya</li>
                        <li><i class=\"ti-mobile\"></i> +254 102 186205</li>
                        <li><i class=\"ti-email\"></i> info@eunccu.org</li>
                    </ul>
                </div>
            </div>
            <div class=\"col-md-6 xs-padding\">
                <div class=\"contact-form\">
                    {% if messages %}
                        <div class=\"container mt-4\">
                            {% for message in messages %}
                                <div class=\"alert alert-{{ message.tags }} alert-dismissible fade show\" role=\"alert\">
                                    {{ message }}
                                </div>
                            {% endfor %}
                        </div>
                    {% endif %}
                    <h3>Drop us a line</h3>
                    <p>Hi. Let's know how we can be of help.</p>
                    <form action=\"\" method=\"post\" class=\"form-horizontal\">
                        {% csrf_token %}
                        <div class=\"form-group colum-row row\">
                            <div class=\"col-sm-6\">
                                <input type=\"text\" id=\"name\" name=\"name\" class=\"form-control\" placeholder=\"Name\" required>
                            </div>
                            <div class=\"col-sm-6\">
                                <input type=\"email\" id=\"email\" name=\"email\" class=\"form-control\" placeholder=\"Email\" required>
                            </div>
                        </div>
                        <div class=\"form-group row\">
                            <div class=\"col-md-12\">
                                <textarea id=\"message\" name=\"message\" cols=\"30\" rows=\"5\" class=\"form-control message\" placeholder=\"Message\" required></textarea>
                            </div>
                        </div>
                        <div class=\"form-group row\">
                            <div class=\"col-md-12\">
                                <button type=\"submit\" class=\"default-btn\">Send Message</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</section><!-- /Contact Section -->
{% endblock %}

{% block extra_js %}
<script>
    document.addEventListener(\"DOMContentLoaded\", function () {
        const alerts = document.querySelectorAll(\".alert\");
        alerts.forEach(function (alert) {
            setTimeout(() => {
                alert.classList.remove(\"show\");
                alert.classList.add(\"fade\");
                setTimeout(() => alert.remove(), 500);
            }, 4000);
        });
    });
</script>
{% endblock %}
""",
    'login.html': """{% extends 'website/base.html' %}
{% load static %}

{% block title %}Login | EUNCCU{% endblock %}

{% block extra_css %}
<style>
:root {
    --primary-green: #2c8e22;
    --primary-red: #ff0019;
    --text-dark: #000000;
    --text-mid: #333333;
    --border: #cccccc;
    --input-bg: #ffffff;
}

.main-content {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 130px);
    padding: 48px 20px 64px;
}

.form-container2 {
    width: 100%;
    max-width: 780px;
    background: #ffffff;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(26, 92, 42, 0.15);
    border: 1px solid rgba(26, 92, 42, 0.12);
    overflow: hidden;
}

.login-header {
    background: linear-gradient(135deg, var(--primary-green) 0%, rgba(0, 107, 27, 0.83) 100%);
    padding: 40px 40px 32px;
    text-align: center;
}

.login-header h2 {
    color: #fff;
    font-size: 1.8rem;
    margin-bottom: 8px;
}

.login-header p {
    color: rgba(255,255,255,0.72);
    margin: 0;
}

.login-body {
    padding: 28px 36px 36px;
}

.field {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
}

.field label {
    font-weight: 600;
    color: var(--text-mid);
    font-size: 0.88rem;
}

.field input {
    padding: 12px 14px;
    border: 1.5px solid #d1d5db;
    border-radius: 10px;
    background: var(--input-bg);
    font-size: 0.95rem;
}

.forgot-link {
    display: block;
    margin-bottom: 20px;
    text-align: right;
    color: var(--primary-green);
    text-decoration: none;
}

.btn-login {
    width: 100%;
    padding: 13px;
    border-radius: 10px;
    border: none;
    background: linear-gradient(135deg, var(--primary-green), rgba(0, 148, 37, 0.9));
    color: white;
    font-weight: 600;
    cursor: pointer;
}

.alert {
    padding: 12px 14px;
    border-radius: 10px;
    margin-bottom: 16px;
}

.alert-success {
    background: #d4edda;
    color: #2c8e22;
}

.alert-error,
.alert-danger {
    background: #ffe6e6;
    color: #c70039;
}

@media (max-width: 576px) {
    .login-body { padding: 24px 22px 28px; }
    .login-header { padding: 32px 22px 28px; }
}
</style>
{% endblock %}

{% block content %}
<div class="header-height"></div>
<div class="main-content">
    <div class="form-container2">
        <div class="login-header">
            <img src="{% static 'img/logo2.png' %}" alt="EUNCCU Logo" style="width: 76px; height: 76px; border-radius: 50%; border: 3px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.1); margin-bottom: 14px;">
            <h2>Welcome Back</h2>
            <p>Sign in to your EUNCCU account</p>
        </div>
        <div class="login-body">
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}" role="alert">{{ message }}</div>
                {% endfor %}
            {% endif %}
            <form method="post" action="">
                {% csrf_token %}
                <div class="field">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="you@example.com" required>
                </div>
                <div class="field">
                    <label for="loginPassword">Password</label>
                    <input type="password" id="loginPassword" name="password" placeholder="Enter your password" required>
                </div>
                {% if next %}
                    <input type="hidden" name="next" value="{{ next }}">
                {% endif %}
                <a href="{% url 'auth_utils:password_reset' %}" class="forgot-link">Forgot password?</a>
                <button type="submit" class="btn-login">Sign In</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.alert').forEach(function (alert) {
            setTimeout(function () {
                alert.style.transition = 'opacity 0.4s ease';
                alert.style.opacity = '0';
                setTimeout(function () { alert.remove(); }, 400);
            }, 4000);
        });
    });
</script>
{% endblock %}
""",
    'edit_profile.html': """{% extends 'website/base.html' %}
{% load static %}

{% block title %}Edit Profile | EUNCCU{% endblock %}

{% block extra_css %}
<style>
:root {
    --primary-green: #2c8e22;
    --secondary-red: #ff0019;
    --dark-text: #000000;
    --border-color: #cccccc;
}

.content-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 15px;
}

.edit-header {
    background: linear-gradient(135deg, var(--primary-green) 0%, rgba(26, 92, 42, 0.95) 100%);
    color: white;
    padding: 3rem 0;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(26, 92, 42, 0.25);
}

.edit-header h1 { margin: 0; font-size: 2rem; }
.edit-header p { margin-top: 0.5rem; opacity: 0.95; }

.edit-form-section {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}

.form-wrapper { padding: 2.5rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }
.form-row.full { grid-template-columns: 1fr; }
.form-group { display: flex; flex-direction: column; }
.form-label { font-size: 0.9rem; font-weight: 600; color: var(--dark-text); margin-bottom: 0.75rem; text-transform: uppercase; }
.form-label.required::after { content: ' *'; color: var(--secondary-red); }
.form-control { padding: 0.875rem; border: 2px solid var(--border-color); border-radius: 8px; background: white; }
.form-control:focus { outline: none; border-color: var(--primary-green); box-shadow: 0 0 0 3px rgba(44, 142, 34, 0.1); }

.profile-picture-group { background: linear-gradient(135deg, rgba(26,92,42,0.08), rgba(220,53,69,0.05)); padding: 2rem; border-radius: 8px; text-align: center; border: 2px dashed var(--border-color); }
.profile-pic-thumbnail { width: 120px; height: 120px; border-radius: 8px; object-fit: cover; border: 3px solid var(--primary-green); margin-bottom: 1rem; }
.default-pic-placeholder { width: 120px; height: 120px; border-radius: 8px; background: linear-gradient(135deg, var(--primary-green), rgba(26,92,42,0.6)); margin: 0 auto 1rem; display:flex; align-items:center; justify-content:center; font-size:2.5rem; border: 3px solid var(--primary-green); }

.section-title { font-size: 1.2rem; font-weight: 600; color: var(--dark-text); margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid var(--primary-green); display:flex; align-items:center; gap:0.75rem; }
.section-title i { color: var(--primary-green); }

.alert { padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1.5rem; }
.alert-success { background: #d4edda; border: 1px solid #c3e6cb; color: #2c8e22; }
.alert-error { background: #f8d7da; border: 1px solid #f5c6cb; color: #ff0019; }

.form-actions { display:flex; gap:1rem; padding-top: 2rem; border-top: 1px solid var(--border-color); }
.btn { padding: 0.875rem 2rem; border-radius: 8px; border:none; font-weight: 600; cursor:pointer; }
.btn-primary { background: var(--primary-green); color: white; flex:1; }
.btn-secondary { background: #95a5a6; color:white; flex:1; }

@media (max-width:768px) { .form-row{grid-template-columns:1fr;} .form-actions{flex-direction:column;} .btn{width:100%;} }
</style>
{% endblock %}

{% block content %}
<div class="header-height"></div>
<div class="content-container">
    <div class="edit-header">
        <h1><i class="fa fa-user-circle"></i> Edit Your Profile</h1>
        <p>Update your personal information and profile picture</p>
    </div>
    <div class="edit-form-section">
        <div class="form-wrapper">
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">
                        <i class="fa fa-{% if message.tags == 'success' %}check-circle{% elif message.tags == 'error' %}exclamation-circle{% else %}info-circle{% endif %}"></i>
                        <div>{{ message }}</div>
                    </div>
                {% endfor %}
            {% endif %}

            <form method="POST" enctype="multipart/form-data">
                {% csrf_token %}
                <div class="form-row">
                    <div class="form-group">
                        <label for="full_name" class="form-label required">Full Name</label>
                        <input type="text" class="form-control" id="full_name" name="full_name" value="{{ user.full_name }}" placeholder="Enter your full name" required>
                    </div>
                    <div class="form-group">
                        <label for="username" class="form-label required">Username</label>
                        <input type="text" class="form-control" id="username" name="username" value="{{ user.username }}" placeholder="Your username" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="email" class="form-label required">Email Address</label>
                        <input type="email" class="form-control" id="email" name="email" value="{{ user.email }}" placeholder="your.email@example.com" required>
                    </div>
                    <div class="form-group">
                        <label for="phone" class="form-label">Phone Number</label>
                        <input type="tel" class="form-control" id="phone" name="phone" value="{{ user.phone }}" placeholder="+254 7XX XXX XXX">
                    </div>
                </div>
                <div class="section-title"><i class="fa fa-graduation-cap"></i> Academic Information</div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="registrationNumber" class="form-label">Registration Number</label>
                        <input type="text" class="form-control" id="registrationNumber" name="registrationNumber" value="{{ user.registrationNumber }}" placeholder="Your registration number">
                    </div>
                    <div class="form-group">
                        <label for="homeCounty" class="form-label">Home County</label>
                        <input type="text" class="form-control" id="homeCounty" name="homeCounty" value="{{ user.homeCounty }}" placeholder="Your home county">
                    </div>
                </div>
                <div class="section-title"><i class="fa fa-image"></i> Profile Picture</div>
                <div class="form-row full">
                    <div class="profile-picture-group">
                        <div class="profile-picture-preview">
                            {% if user.profile_picture %}
                                <img src="{{ user.profile_picture.url }}" alt="Current Profile Picture" class="profile-pic-thumbnail">
                                <div class="file-info">Current: {{ user.profile_picture.name|truncatechars:30 }}</div>
                            {% else %}
                                <div class="default-pic-placeholder">📸</div>
                                <div class="file-info">No profile picture uploaded yet</div>
                            {% endif %}
                        </div>
                        <label for="profile_picture" class="btn btn-primary" style="display:inline-block; padding:0.85rem 1.25rem;">Choose Photo</label>
                        <input type="file" class="form-control" id="profile_picture" name="profile_picture" accept="image/*" style="display:none;">
                        <div class="file-info" style="margin-top: 1rem; color:#555;">JPG, PNG or GIF (Max 5MB)</div>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                    <a href="{% url 'website:profile' %}" class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    const profileInput = document.getElementById('profile_picture');
    if (profileInput) {
        profileInput.addEventListener('change', function (e) {
            if (e.target.files[0]) {
                const fileSize = (e.target.files[0].size / 1024 / 1024).toFixed(2);
                const preview = document.querySelector('.profile-picture-preview');
                const fileName = e.target.files[0].name;
                const reader = new FileReader();
                reader.onload = function (event) {
                    preview.innerHTML = `\n                        <img src="${event.target.result}" alt="Preview" class="profile-pic-thumbnail">\n                        <div class="file-info">New: ${fileName} (${fileSize}MB)</div>\n                    `;
                };
                reader.readAsDataURL(e.target.files[0]);
            }
        });
    }
</script>
{% endblock %}
""",
    'profile.html': """{% extends 'website/base.html' %}
{% load static %}

{% block title %}My Profile | EUNCCU{% endblock %}

{% block extra_css %}
<style>
:root {
    --primary-green: #2c8e22;
    --secondary-red: #ff0019;
    --dark-text: #000000;
    --light-text: #333333;
    --border-color: #cccccc;
}

.content-container { max-width: 1200px; margin: 0 auto; padding: 0 15px; }
.profile-header { background: linear-gradient(135deg, var(--primary-green) 0%, rgba(26, 92, 42, 0.95) 100%); color: white; padding: 3rem 0; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(26, 92, 42, 0.25); }
.profile-header h1 { margin: 0; font-size: 2.5rem; }
.profile-header p { margin-top: 0.5rem; opacity: 0.95; }
.main-profile-section { background: white; border-radius: 12px; box-shadow: 0 2px 16px rgba(0,0,0,0.08); overflow: hidden; margin-bottom: 2rem; }
.profile-top { display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; padding: 2.5rem; align-items: start; }
.profile-picture-section { text-align: center; }
.profile-avatar, .default-avatar { width: 200px; height: 200px; margin: 0 auto 1.5rem; border-radius: 12px; border: 4px solid var(--primary-green); box-shadow: 0 4px 12px rgba(44, 142, 34, 0.2); }
.default-avatar { display:flex; align-items:center; justify-content:center; background: linear-gradient(135deg, var(--primary-green), rgba(26,92,42,0.7)); font-size: 4rem; }
.btn-edit-profile, .btn-user-manager { background-color: var(--primary-green); color: white; border:none; padding:0.75rem 2rem; border-radius:8px; font-size:1rem; font-weight:600; text-decoration:none; display:inline-flex; align-items:center; gap:0.5rem; }
.btn-edit-profile:hover, .btn-user-manager:hover { background-color: var(--secondary-red); }
.info-group { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:1.5rem; }
.info-item { display:flex; flex-direction:column; }
.info-label { font-size:0.85rem; font-weight:600; color: var(--light-text); text-transform:uppercase; margin-bottom:0.5rem; }
.info-value { font-size:1.1rem; font-weight:500; color: var(--dark-text); word-break:break-all; }
.info-value.highlight { color: var(--primary-green); font-weight:600; }
.divider { height:1px; background-color: var(--border-color); margin:1.5rem 0; }
.profile-footer { padding:2rem 2.5rem; background:white; border-top:1px solid var(--border-color); display:flex; gap:1rem; justify-content:flex-end; }
@media (max-width:768px) { .profile-top { grid-template-columns:1fr; padding:1.5rem; } .info-group { grid-template-columns:1fr; } .profile-footer { flex-direction:column; align-items:stretch; } }
</style>
{% endblock %}

{% block content %}
<div class="header-height"></div>
<div class="content-container">
    <div class="profile-header">
        <div>
            <h1>My Profile</h1>
            <p>Manage and view your account information</p>
        </div>
    </div>

    {% if request.user.is_authenticated %}
        <div class="main-profile-section">
            <div class="profile-top">
                <div class="profile-picture-section">
                    {% if request.user.profile_picture %}
                        <img src="{{ request.user.profile_picture.url }}" alt="Profile Picture" class="profile-avatar">
                    {% else %}
                        <div class="default-avatar">👤</div>
                    {% endif %}
                    <a href="{% url 'website:edit_profile' %}" class="btn-edit-profile"><i class="fa fa-pencil"></i> Edit Profile</a>
                </div>
                <div>
                    <div class="info-group">
                        <div class="info-item">
                            <span class="info-label">Full Name</span>
                            <span class="info-value highlight">{{ request.user.full_name|default:"Not Set" }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Username</span>
                            <span class="info-value">{{ request.user.username }}</span>
                        </div>
                    </div>
                    <div class="info-group">
                        <div class="info-item">
                            <span class="info-label">Email Address</span>
                            <span class="info-value">{{ request.user.email }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Phone Number</span>
                            <span class="info-value">{{ request.user.phone|default:"Not Set" }}</span>
                        </div>
                    </div>
                    <div class="divider"></div>
                    <div class="info-group">
                        <div class="info-item">
                            <span class="info-label">Registration Number</span>
                            <span class="info-value">{{ request.user.registrationNumber|default:"Not Set" }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Home County</span>
                            <span class="info-value">{{ request.user.homeCounty|default:"Not Set" }}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="profile-footer">
                {% for group in request.user.groups.all %}
                    {% if group.name == "User Manager" %}
                        <a href="{% url 'website:user_manager_dashboard' %}" class="btn-user-manager"><i class="fa fa-users"></i> User Manager</a>
                    {% endif %}
                {% endfor %}
                <a href="{% url 'website:edit_profile' %}" class="btn-edit-profile"><i class="fa fa-pencil"></i> Edit Profile</a>
            </div>
        </div>
    {% else %}
        <div style="background:#fff; border-radius:12px; padding:2rem; box-shadow:0 2px 16px rgba(0,0,0,0.08);">
            <div style="color:#c70039; font-weight:700; margin-bottom:1rem;">You must be logged in to view your profile.</div>
            <a href="{% url 'website:login' %}" style="color: var(--primary-green); font-weight:600; text-decoration:underline;">Click here to login</a>
        </div>
    {% endif %}
</div>
{% endblock %}
""",
    'base2.html': """{% extends 'website/base.html' %}
{% load static %}

{% block title %}Contact Us | EUNCCU{% endblock %}

{% block content %}
<div class=\"header-height\"></div>

<div class=\"pager-header\">
    <div class=\"container\">
        <div class=\"page-content\">
            <h2>Contact Us</h2>
            <p>Do You Have a Question, Inquiry or Comment? Then Get in touch with us !</p>
            <ol class=\"breadcrumb\">
                <li class=\"breadcrumb-item\"><a href=\"{% url 'website:home' %}\">Home</a></li>
                <li class=\"breadcrumb-item active\">Contact</li>
            </ol>
        </div>
    </div>
</div><!-- /Page Header -->

<section class=\"contact-section padding\">
    <iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d249.35858427533262!2d35.93165600603046!3d-0.365030430931147!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x18298752c9fed347%3A0xfcf061f5ffb07c68!2sEgerton%20B1%20Church!5e0!3m2!1sen!2ske!4v1723058489533!5m2!1sen!2ske\"
        width=\"100%\" height=\"450\" style=\"border:0px solid #000000;\" allowfullscreen=\"\" loading=\"lazy\"
        referrerpolicy=\"no-referrer-when-downgrade\"></iframe>
    <div class=\"container\">
        <div class=\"row contact-wrap\">
            <div class=\"col-md-6 xs-padding\">
                <div class=\"contact-info\">
                    <h3>Get in touch</h3>
                    <p>We’re here to assist you with any questions or inquiries you may have. Feel free to reach out to us for more information about our services, suggestions, or assistance.</p>
                    <ul>
                        <li><i class=\"ti-location-pin\"></i> Egerton University, Njoro, Nakuru-Kenya</li>
                        <li><i class=\"ti-mobile\"></i> +254 102 186205</li>
                        <li><i class=\"ti-email\"></i> info@eunccu.org</li>
                    </ul>
                </div>
            </div>
            <div class=\"col-md-6 xs-padding\">
                <div class=\"contact-form\">
                    {% if messages %}
                        <div class=\"container mt-4\">
                            {% for message in messages %}
                                <div class=\"alert alert-{{ message.tags }} alert-dismissible fade show\" role=\"alert\">
                                    {{ message }}
                                </div>
                            {% endfor %}
                        </div>
                    {% endif %}
                    <h3>Drop us a line</h3>
                    <p>Hi. Let's know how we can be of help.</p>
                    <form action=\"\" method=\"post\" class=\"form-horizontal\">
                        {% csrf_token %}
                        <div class=\"form-group colum-row row\">
                            <div class=\"col-sm-6\">
                                <input type=\"text\" id=\"name\" name=\"name\" class=\"form-control\" placeholder=\"Name\" required>
                            </div>
                            <div class=\"col-sm-6\">
                                <input type=\"email\" id=\"email\" name=\"email\" class=\"form-control\" placeholder=\"Email\" required>
                            </div>
                        </div>
                        <div class=\"form-group row\">
                            <div class=\"col-md-12\">
                                <textarea id=\"message\" name=\"message\" cols=\"30\" rows=\"5\" class=\"form-control message\" placeholder=\"Message\" required></textarea>
                            </div>
                        </div>
                        <div class=\"form-group row\">
                            <div class=\"col-md-12\">
                                <button type=\"submit\" class=\"default-btn\">Send Message</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}
""",
}

for name, content in files.items():
    path = root / name
    path.write_text(content, encoding='utf-8')
    print(f'Wrote {path}')
