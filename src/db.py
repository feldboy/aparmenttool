"""
Database connection and schema definitions for RealtyScanner Agent

This module provides:
1. MongoDB connection utilities
2. Pydantic models for data validation
3. Database initialization and migration scripts
4. CRUD operations for all collections
"""

import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pydantic import BaseModel, Field
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string")

class NotificationChannel(str, Enum):
    """Supported notification channels"""
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    EMAIL = "email"

class ListingSource(str, Enum):
    """Supported listing sources"""
    YAD2 = "Yad2"
    FACEBOOK = "Facebook"

# Pydantic Models for MongoDB Collections

class LocationCriteria(BaseModel):
    """Location filtering criteria"""
    city: str
    neighborhoods: List[str] = []
    streets: List[str] = []

class PriceRange(BaseModel):
    """Price range criteria"""
    min: int
    max: int

class RoomRange(BaseModel):
    """Room count criteria"""
    min: float
    max: float

class ScanTargets(BaseModel):
    """Scan target URLs and IDs"""
    yad2_url: Optional[str] = None
    facebook_group_ids: List[str] = []

class NotificationChannelConfig(BaseModel):
    """Individual notification channel configuration"""
    enabled: bool = False
    telegram_chat_id: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None
    email_address: Optional[str] = None

class NotificationChannels(BaseModel):
    """All notification channel configurations"""
    telegram: NotificationChannelConfig = NotificationChannelConfig()
    whatsapp: NotificationChannelConfig = NotificationChannelConfig()
    email: NotificationChannelConfig = NotificationChannelConfig()

class ScanState(BaseModel):
    """Tracking state for each scan target"""
    last_post_timestamp: Optional[datetime] = None
    last_scan_timestamp: Optional[datetime] = None

class UserProfile(BaseModel):
    """User search profile model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    profile_name: str
    is_active: bool = True
    location_criteria: LocationCriteria
    price: PriceRange
    rooms: RoomRange
    property_type: List[str] = ["דירה", "סטודיו"]
    scan_targets: ScanTargets
    notification_channels: NotificationChannels
    last_scan_state: Dict[str, ScanState] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ScannedListing(BaseModel):
    """Scanned listing model for duplicate prevention"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    listing_id: str  # Platform-specific ID
    source: ListingSource
    content_hash: str  # SHA256 hash of core content
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    url: str
    raw_data: Dict[str, Any] = {}  # Store original scraped data

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SentNotification(BaseModel):
    """Sent notification log model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    # Allow profile_id to be an ObjectId or any type to avoid validation errors
    profile_id: Any
    listing_id: str
    channel: NotificationChannel
    recipient: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    message_content: str
    success: bool = True
    error_message: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class FacebookCredentials(BaseModel):
    """Facebook credentials model for group scanning"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    telegram_chat_id: str
    email: str
    password: str  # Should be encrypted in production
    groups: List[str] = []  # List of Facebook group URLs or names
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DatabaseManager:
    """MongoDB database manager"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.user_profiles: Optional[Collection] = None
        self.scanned_listings: Optional[Collection] = None
        self.sent_notifications: Optional[Collection] = None
        self.search_profiles: Optional[Collection] = None
        self.facebook_credentials: Optional[Collection] = None
        
    def connect(self) -> bool:
        """Connect to MongoDB database"""
        try:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            database_name = os.getenv("MONGODB_DATABASE", "realty_scanner")
            
            self.client = MongoClient(mongodb_uri)
            
            # Test the connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB at {mongodb_uri}")
            
            self.db = self.client[database_name]
            
            # Initialize collections
            self.user_profiles = self.db.user_profiles
            self.scanned_listings = self.db.scanned_listings
            self.sent_notifications = self.db.sent_notifications
            self.search_profiles = self.db.search_profiles
            self.facebook_credentials = self.db.facebook_credentials
            
            # Create indexes for better performance
            self._create_indexes()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # User profiles indexes
            self.user_profiles.create_index("profile_name")
            self.user_profiles.create_index("is_active")
            
            # Scanned listings indexes
            self.scanned_listings.create_index([("listing_id", 1), ("source", 1)], unique=True)
            self.scanned_listings.create_index("content_hash")
            self.scanned_listings.create_index("first_seen")
            
            # Sent notifications indexes
            self.sent_notifications.create_index("profile_id")
            self.sent_notifications.create_index("listing_id")
            self.sent_notifications.create_index("sent_at")
            self.sent_notifications.create_index([("channel", 1), ("recipient", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    # User Profile CRUD Operations
    
    def create_user_profile(self, profile: UserProfile) -> Optional[str]:
        """Create a new user profile"""
        try:
            profile.updated_at = datetime.utcnow()
            result = self.user_profiles.insert_one(profile.dict(by_alias=True, exclude={"id"}))
            logger.info(f"Created user profile: {profile.profile_name}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            return None
    
    def get_user_profile(self, profile_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        try:
            doc = self.user_profiles.find_one({"_id": ObjectId(profile_id)})
            if doc:
                return UserProfile(**doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile {profile_id}: {e}")
            return None
    
    def get_active_user_profiles(self) -> List[UserProfile]:
        """Get all active user profiles"""
        try:
            docs = self.user_profiles.find({"is_active": True})
            return [UserProfile(**doc) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get active user profiles: {e}")
            return []
    
    def update_user_profile(self, profile_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            updates["updated_at"] = datetime.utcnow()
            result = self.user_profiles.update_one(
                {"_id": ObjectId(profile_id)}, 
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user profile {profile_id}: {e}")
            return False
    
    # Scanned Listing CRUD Operations
    
    def is_listing_seen(self, listing_id: str, source: ListingSource) -> bool:
        """Check if listing has been seen before"""
        try:
            doc = self.scanned_listings.find_one({
                "listing_id": listing_id,
                "source": source.value
            })
            return doc is not None
        except Exception as e:
            logger.error(f"Failed to check if listing {listing_id} seen: {e}")
            return False
    
    def add_scanned_listing(self, listing: ScannedListing) -> Optional[str]:
        """Add new scanned listing"""
        try:
            result = self.scanned_listings.insert_one(listing.dict(by_alias=True, exclude={"id"}))
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to add scanned listing {listing.listing_id}: {e}")
            return None
    
    # Notification CRUD Operations
    
    def log_sent_notification(self, notification: SentNotification) -> Optional[str]:
        """Log sent notification"""
        try:
            result = self.sent_notifications.insert_one(notification.dict(by_alias=True, exclude={"id"}))
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to log notification: {e}")
            return None
    
    def get_recent_notifications(self, limit: int = 50) -> List[SentNotification]:
        """Get recent notifications"""
        try:
            docs = self.sent_notifications.find().sort("sent_at", -1).limit(limit)
            return [SentNotification(**doc) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get recent notifications: {e}")
            return []

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> DatabaseManager:
    """Get database manager instance"""
    if not db_manager.client:
        db_manager.connect()
    return db_manager
