CREATE DATABASE IF NOT EXISTS arunachal_tourism;
USE arunachal_tourism;

-- Users table for authentication
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('tourist', 'guide', 'admin') NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guides profile table
CREATE TABLE guides (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    specialization VARCHAR(200),
    experience_years INT,
    languages_spoken VARCHAR(200),
    location VARCHAR(100),
    price_per_day DECIMAL(10,2),
    availability_status ENUM('available', 'busy') DEFAULT 'available',
    rating DECIMAL(3,2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tourist bookings table
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tourist_id INT,
    guide_id INT,
    tourist_name VARCHAR(100),
    native_place VARCHAR(100),
    phone VARCHAR(15),
    days_to_stay INT,
    arrival_date DATE,
    departure_date DATE,
    booking_status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tourist_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (guide_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Events and photos uploaded by guides
CREATE TABLE guide_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guide_id INT,
    upload_type ENUM('event', 'photo', 'location') NOT NULL,
    title VARCHAR(200),
    description TEXT,
    image_path VARCHAR(500),
    location VARCHAR(200),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guide_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert default admin user
INSERT INTO users (username, password, user_type, full_name, email) 
VALUES ('admin', 'admin123', 'admin', 'System Administrator', 'admin@arunachaltourism.com');
