#!/bin/bash

echo "🔄 Moving FlintWeatherAI to shared storage..."
echo ""

# Check if storage is accessible
if [ ! -d ~/storage/shared ]; then
    echo "❌ Storage not set up. Run: termux-setup-storage"
    exit 1
fi

# Remove old shared storage version if exists
if [ -d ~/storage/shared/FlintWeatherAI ]; then
    echo "📦 Removing old version in shared storage..."
    rm -rf ~/storage/shared/FlintWeatherAI
fi

# Copy to shared storage (exclude venv and cache)
echo "📋 Copying project to shared storage..."
rsync -av --exclude='venv' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='.git/objects' \
          ~/FlintWeatherAI/ ~/storage/shared/FlintWeatherAI/

# Verify copy
if [ -d ~/storage/shared/FlintWeatherAI ]; then
    echo "✅ Copy successful!"
    
    # Backup Termux version
    BACKUP_NAME="FlintWeatherAI_backup_$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up Termux version to ~/$BACKUP_NAME..."
    mv ~/FlintWeatherAI ~/$BACKUP_NAME
    
    # Create symlink
    echo "🔗 Creating symlink..."
    ln -s ~/storage/shared/FlintWeatherAI ~/FlintWeatherAI
    
    # Verify
    if [ -L ~/FlintWeatherAI ]; then
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "📍 Locations:"
        echo "  - Real files: ~/storage/shared/FlintWeatherAI"
        echo "  - Android: /storage/emulated/0/FlintWeatherAI"
        echo "  - Termux: ~/FlintWeatherAI (symlink)"
        echo "  - Backup: ~/$BACKUP_NAME"
        echo ""
        echo "🔍 Symlink verification:"
        ls -la ~ | grep -E "FlintWeatherAI|$BACKUP_NAME"
        echo ""
        echo "📊 Project size:"
        du -sh ~/storage/shared/FlintWeatherAI
        echo ""
        echo "⚠️  Note: You'll need to reinstall venv in shared storage:"
        echo "  cd ~/FlintWeatherAI"
        echo "  python -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -r requirements.txt"
    else
        echo "❌ Failed to create symlink"
        # Restore backup
        mv ~/$BACKUP_NAME ~/FlintWeatherAI
        echo "Restored backup"
    fi
else
    echo "❌ Copy failed!"
fi
