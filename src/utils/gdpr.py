"""
GDPR Compliance Utilities
"""
import logging
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class GDPRManager:
    """Manages GDPR compliance features"""
    
    def __init__(self):
        self.consent_file = Path("data/user_consent.json")
        self.consent_file.parent.mkdir(exist_ok=True)
        
        # Encryption key (in production, store securely)
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        
        logger.info("GDPR manager initialized")
    
    def _get_or_create_key(self):
        """Get or create encryption key"""
        key_file = Path("data/.key")
        
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to load encryption key: {e}")
        
        # Create new key
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("New encryption key created")
        except Exception as e:
            logger.error(f"Failed to save encryption key: {e}")
        
        return key
    
    def record_consent(self, user_id, consent_type, granted=True):
        """Record user consent"""
        try:
            consent_data = self._load_consent_data()
            
            if user_id not in consent_data:
                consent_data[user_id] = {}
            
            consent_data[user_id][consent_type] = {
                'granted': granted,
                'timestamp': datetime.now().isoformat(),
                'ip_hash': self._hash_ip("127.0.0.1"),  # Placeholder
                'version': "1.0"
            }
            
            self._save_consent_data(consent_data)
            
            logger.info(f"Consent recorded: {user_id} - {consent_type} - {granted}")
            
        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
    
    def check_consent(self, user_id, consent_type):
        """Check if user has granted specific consent"""
        try:
            consent_data = self._load_consent_data()
            
            if user_id in consent_data and consent_type in consent_data[user_id]:
                return consent_data[user_id][consent_type]['granted']
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check consent: {e}")
            return False
    
    def get_user_consents(self, user_id):
        """Get all consents for a user"""
        try:
            consent_data = self._load_consent_data()
            return consent_data.get(user_id, {})
            
        except Exception as e:
            logger.error(f"Failed to get user consents: {e}")
            return {}
    
    def revoke_consent(self, user_id, consent_type):
        """Revoke specific consent"""
        self.record_consent(user_id, consent_type, granted=False)
        logger.info(f"Consent revoked: {user_id} - {consent_type}")
    
    def delete_user_data(self, user_id):
        """Delete all data for a user (right to be forgotten)"""
        try:
            # This would delete user data from database
            # For now, just log the request
            
            logger.info(f"Data deletion requested for user: {user_id}")
            
            # Remove consent records
            consent_data = self._load_consent_data()
            if user_id in consent_data:
                del consent_data[user_id]
                self._save_consent_data(consent_data)
            
            # In production, would also:
            # 1. Delete from database
            # 2. Remove from cloud storage
            # 3. Notify external services
            # 4. Log the deletion
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user data: {e}")
            return False
    
    def export_user_data(self, user_id):
        """Export all user data (data portability)"""
        try:
            # In production, this would gather data from all sources
            user_data = {
                'user_id': user_id,
                'export_date': datetime.now().isoformat(),
                'consents': self.get_user_consents(user_id),
                'data': {
                    'note': 'User data would be exported from database here'
                }
            }
            
            logger.info(f"Data export requested for user: {user_id}")
            return user_data
            
        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            return None
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data"""
        try:
            if isinstance(data, str):
                data = data.encode()
            elif not isinstance(data, bytes):
                data = json.dumps(data).encode()
            
            encrypted = self.cipher.encrypt(data)
            return encrypted
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            return None
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data)
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            return None
    
    def anonymize_data(self, data, fields_to_anonymize):
        """Anonymize specified fields in data"""
        try:
            anonymized = data.copy()
            
            for field in fields_to_anonymize:
                if field in anonymized:
                    # Replace with hash
                    original_value = str(anonymized[field])
                    anonymized[field] = hashlib.sha256(original_value.encode()).hexdigest()[:16]
            
            return anonymized
            
        except Exception as e:
            logger.error(f"Failed to anonymize data: {e}")
            return data
    
    def _load_consent_data(self):
        """Load consent data from file"""
        try:
            if self.consent_file.exists():
                with open(self.consent_file, 'r') as f:
                    return json.load(f)
            return {}
            
        except Exception as e:
            logger.error(f"Failed to load consent data: {e}")
            return {}
    
    def _save_consent_data(self, data):
        """Save consent data to file"""
        try:
            with open(self.consent_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save consent data: {e}")
    
    def _hash_ip(self, ip_address):
        """Hash IP address for privacy"""
        return hashlib.sha256(ip_address.encode()).hexdigest()
    
    def get_required_consents(self):
        """Get list of required consents"""
        return [
            'data_collection',
            'data_processing', 
            'data_storage',
            'analytics',
            'performance_monitoring'
        ]
    
    def generate_privacy_report(self, user_id):
        """Generate privacy compliance report for user"""
        try:
            consents = self.get_user_consents(user_id)
            required_consents = self.get_required_consents()
            
            report = {
                'user_id': user_id,
                'report_date': datetime.now().isoformat(),
                'gdpr_compliant': True,
                'consents': {
                    'total_required': len(required_consents),
                    'granted': 0,
                    'missing': []
                },
                'data_retention': {
                    'policy': '30 days',
                    'encryption': True,
                    'anonymization': True
                }
            }
            
            for consent in required_consents:
                if consent in consents and consents[consent]['granted']:
                    report['consents']['granted'] += 1
                else:
                    report['consents']['missing'].append(consent)
            
            # Check if fully compliant
            if report['consents']['missing']:
                report['gdpr_compliant'] = False
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate privacy report: {e}")
            return None

# Global GDPR manager instance
gdpr_manager = GDPRManager()

def get_gdpr_manager():
    """Get global GDPR manager instance"""
    return gdpr_manager
