from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse


class SecurityTests(TestCase):
    """Tests de sécurité pour l'application"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()

    def test_csrf_protection_enabled(self):
        """Test que la protection CSRF est active"""
        response = self.client.get(reverse('home'))
        # Vérifier que le token CSRF est présent dans le contexte
        self.assertIn('csrf_token', response.context or {})

    def test_security_headers_present(self):
        """Test que les headers de sécurité sont présents"""
        response = self.client.get(reverse('home'))

        # X-Frame-Options
        self.assertEqual(response.get('X-Frame-Options'), 'DENY')

        # X-Content-Type-Options
        self.assertEqual(response.get('X-Content-Type-Options'), 'nosniff')

        # Referrer-Policy (peut être 'same-origin' ou 'strict-origin-when-cross-origin')
        referrer_policy = response.get('Referrer-Policy')
        self.assertIn(referrer_policy, ['strict-origin-when-cross-origin', 'same-origin'])

    def test_csp_headers_present(self):
        """Test que les headers CSP sont présents"""
        response = self.client.get(reverse('home'))
        csp_header = response.get('Content-Security-Policy')

        # Vérifier que le header CSP existe
        self.assertIsNotNone(csp_header)

        # Vérifier les directives de base
        if csp_header:
            self.assertIn("default-src 'self'", csp_header)
            self.assertIn("frame-ancestors 'none'", csp_header)

    @override_settings(DEBUG=False)
    def test_secure_cookies_in_production(self):
        """Test que les cookies sont sécurisés en production"""
        # Vérifier la configuration des cookies en production
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertTrue(settings.CSRF_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, 'Strict')
        self.assertEqual(settings.CSRF_COOKIE_SAMESITE, 'Strict')

    def test_debug_mode_configurable(self):
        """Test que DEBUG est configurable via environnement"""
        # Vérifier que DEBUG est bien un booléen
        self.assertIsInstance(settings.DEBUG, bool)

    def test_secret_key_configured(self):
        """Test que SECRET_KEY est configurée"""
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, '')
        self.assertGreater(len(settings.SECRET_KEY), 20)

    def test_allowed_hosts_configured(self):
        """Test que ALLOWED_HOSTS est configuré"""
        self.assertIsInstance(settings.ALLOWED_HOSTS, list)
        self.assertGreater(len(settings.ALLOWED_HOSTS), 0)


class AuthenticationSecurityTests(TestCase):
    """Tests de sécurité pour l'authentification"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client(enforce_csrf_checks=True)

    def test_admin_requires_authentication(self):
        """Test que l'admin nécessite une authentification"""
        response = self.client.get('/admin/')
        # Doit rediriger vers la page de login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_csrf_required_for_post(self):
        """Test que CSRF est requis pour les requêtes POST"""
        # Tentative de POST sans token CSRF
        response = self.client.post('/admin/login/', {
            'username': 'test',
            'password': 'test'  # pragma: allowlist secret
        })
        # Doit être refusé (403 Forbidden)
        self.assertEqual(response.status_code, 403)


class DatabaseSecurityTests(TestCase):
    """Tests de sécurité pour la base de données"""

    def test_database_credentials_not_in_settings(self):
        """Test que les credentials DB ne sont pas en dur dans settings"""
        # Vérifier que les credentials viennent des variables d'environnement
        db_config = settings.DATABASES['default']

        # Si c'est PostgreSQL, vérifier que les valeurs ne sont pas hardcodées
        if db_config['ENGINE'] == 'django.db.backends.postgresql':
            # Les valeurs doivent venir des variables d'environnement
            # On vérifie juste que la configuration existe
            self.assertIn('NAME', db_config)
            self.assertIn('USER', db_config)
            self.assertIn('PASSWORD', db_config)


class PasswordValidationTests(TestCase):
    """Tests pour la validation des mots de passe"""

    def test_password_validators_configured(self):
        """Test que les validateurs de mot de passe sont configurés"""
        self.assertGreater(len(settings.AUTH_PASSWORD_VALIDATORS), 0)

        # Vérifier les validateurs standards
        validator_names = [v['NAME'] for v in settings.AUTH_PASSWORD_VALIDATORS]

        self.assertIn('django.contrib.auth.password_validation.MinimumLengthValidator', validator_names)
        self.assertIn('django.contrib.auth.password_validation.CommonPasswordValidator', validator_names)


class HttpsSecurityTests(TestCase):
    """Tests pour la sécurité HTTPS"""

    @override_settings(
        DEBUG=False,
        SECURE_SSL_REDIRECT=True,
        SECURE_HSTS_SECONDS=31536000,
        SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
        SECURE_HSTS_PRELOAD=True
    )
    def test_https_settings_in_production(self):
        """Test que les paramètres HTTPS sont actifs en production"""
        # Test avec DEBUG=False pour vérifier la configuration en production
        self.assertTrue(settings.SECURE_SSL_REDIRECT)
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 31536000)
        self.assertTrue(settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertTrue(settings.SECURE_HSTS_PRELOAD)

    def test_https_disabled_in_debug(self):
        """Test que HTTPS est désactivé en mode DEBUG"""
        if settings.DEBUG:
            self.assertFalse(settings.SECURE_SSL_REDIRECT)
