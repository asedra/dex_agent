"""Migration v005: Software management tables for PostgreSQL."""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def upgrade(conn):
    """Apply migration v005 - Software management tables."""
    cursor = conn.cursor()
    
    try:
        # Create software_packages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS software_packages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                version VARCHAR(100) NOT NULL,
                description TEXT,
                package_type VARCHAR(50) NOT NULL DEFAULT 'exe',
                category VARCHAR(50) DEFAULT 'other',
                vendor VARCHAR(255),
                size_bytes BIGINT,
                download_url TEXT,
                file_path TEXT,
                silent_install_args TEXT,
                silent_uninstall_args TEXT,
                install_script TEXT,
                uninstall_script TEXT,
                dependencies JSONB DEFAULT '[]'::jsonb,
                metadata JSONB DEFAULT '{}'::jsonb,
                requires_reboot BOOLEAN DEFAULT FALSE,
                requires_admin BOOLEAN DEFAULT TRUE,
                signature_verified BOOLEAN DEFAULT FALSE,
                checksum VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, version)
            )
        """)
        
        # Create installed_software table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installed_software (
                id SERIAL PRIMARY KEY,
                agent_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                version VARCHAR(100),
                vendor VARCHAR(255),
                install_date TIMESTAMP,
                install_location TEXT,
                uninstall_string TEXT,
                registry_key TEXT,
                size_bytes BIGINT,
                last_used TIMESTAMP,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        """)
        
        # Create installation_jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installation_jobs (
                id SERIAL PRIMARY KEY,
                agent_id VARCHAR(255) NOT NULL,
                package_id INTEGER,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                scheduled_at TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                progress_percent INTEGER DEFAULT 0,
                current_step TEXT,
                error_message TEXT,
                output_log TEXT,
                rollback_performed BOOLEAN DEFAULT FALSE,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                install_params JSONB DEFAULT '{}'::jsonb,
                created_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
                FOREIGN KEY (package_id) REFERENCES software_packages(id) ON DELETE SET NULL
            )
        """)
        
        # Create software_repositories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS software_repositories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                type VARCHAR(50) NOT NULL,
                url TEXT,
                api_key TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                priority INTEGER DEFAULT 0,
                last_sync TIMESTAMP,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_installed_software_agent_id 
            ON installed_software(agent_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_installed_software_name 
            ON installed_software(name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_installation_jobs_agent_id 
            ON installation_jobs(agent_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_installation_jobs_status 
            ON installation_jobs(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_installation_jobs_package_id 
            ON installation_jobs(package_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_software_packages_type 
            ON software_packages(package_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_software_packages_category 
            ON software_packages(category)
        """)
        
        # Create triggers for updated_at
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        cursor.execute("""
            CREATE TRIGGER update_software_packages_updated_at 
            BEFORE UPDATE ON software_packages 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        """)
        
        cursor.execute("""
            CREATE TRIGGER update_installation_jobs_updated_at 
            BEFORE UPDATE ON installation_jobs 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        """)
        
        cursor.execute("""
            CREATE TRIGGER update_software_repositories_updated_at 
            BEFORE UPDATE ON software_repositories 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        """)
        
        # Insert default repositories
        cursor.execute("""
            INSERT INTO software_repositories (name, type, url, enabled, priority)
            VALUES 
                ('Chocolatey', 'chocolatey', 'https://community.chocolatey.org/api/v2/', true, 0),
                ('Windows Package Manager', 'winget', NULL, true, 1),
                ('Custom Repository', 'custom', NULL, false, 2)
            ON CONFLICT (name) DO NOTHING
        """)
        
        # Insert sample software packages
        cursor.execute("""
            INSERT INTO software_packages (
                name, version, description, package_type, category, vendor,
                silent_install_args, silent_uninstall_args
            )
            VALUES 
                ('Google Chrome', 'latest', 'Fast, secure web browser', 'chocolatey', 
                 'productivity', 'Google', '-y', NULL),
                ('Visual Studio Code', 'latest', 'Code editor', 'winget', 
                 'development', 'Microsoft', '--silent', NULL),
                ('7-Zip', '23.01', 'File archiver', 'exe', 
                 'utilities', 'Igor Pavlov', '/S', '/S'),
                ('Notepad++', '8.6', 'Text editor', 'exe', 
                 'development', 'Don Ho', '/S', '/S')
            ON CONFLICT (name, version) DO NOTHING
        """)
        
        conn.commit()
        logger.info("Migration v005 applied successfully - Software management tables created")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error applying migration v005: {str(e)}")
        raise


def downgrade(conn):
    """Rollback migration v005 - Remove software management tables."""
    cursor = conn.cursor()
    
    try:
        # Drop triggers
        cursor.execute("DROP TRIGGER IF EXISTS update_software_packages_updated_at ON software_packages")
        cursor.execute("DROP TRIGGER IF EXISTS update_installation_jobs_updated_at ON installation_jobs")
        cursor.execute("DROP TRIGGER IF EXISTS update_software_repositories_updated_at ON software_repositories")
        
        # Drop tables
        cursor.execute("DROP TABLE IF EXISTS installation_jobs CASCADE")
        cursor.execute("DROP TABLE IF EXISTS installed_software CASCADE")
        cursor.execute("DROP TABLE IF EXISTS software_packages CASCADE")
        cursor.execute("DROP TABLE IF EXISTS software_repositories CASCADE")
        
        conn.commit()
        logger.info("Migration v005 rolled back successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error rolling back migration v005: {str(e)}")
        raise