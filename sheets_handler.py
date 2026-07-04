import pandas as pd
import io
from typing import List, Dict, Optional
import requests
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsHandler:
    """Handler untuk membaca dan menulis data ke Google Sheets via URL"""
    
    def __init__(self, spreadsheet_id: str, sheet_name: str = "Sheet1"):
        """
        Initialize Google Sheets handler
        
        Args:
            spreadsheet_id: ID dari Google Sheets
            sheet_name: Nama sheet (default: "Sheet1")
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=0"
        self.df = None
        self.load_data()
    
    def load_data(self) -> bool:
        """Load data dari Google Sheets"""
        try:
            self.df = pd.read_csv(self.csv_url)
            logger.info(f"✓ Data berhasil dimuat. Total: {len(self.df)} baris")
            return True
        except Exception as e:
            logger.error(f"✗ Error loading data: {e}")
            return False
    
    def get_all_data(self) -> List[Dict]:
        """Get semua data dalam format list of dictionaries"""
        if self.df is None:
            return []
        return self.df.to_dict('records')
    
    def search_by_title(self, title: str) -> Optional[Dict]:
        """Cari series/film berdasarkan judul (case-insensitive)"""
        if self.df is None:
            return None
        
        result = self.df[self.df['Judul'].str.contains(title, case=False, na=False)]
        
        if not result.empty:
            return result.iloc[0].to_dict()
        return None
    
    def search_by_title_partial(self, title: str) -> List[Dict]:
        """Cari series/film dengan partial match"""
        if self.df is None:
            return []
        
        results = self.df[self.df['Judul'].str.contains(title, case=False, na=False)]
        return results.to_dict('records')
    
    def get_by_status(self, status: str) -> List[Dict]:
        """Get semua series/film berdasarkan status"""
        if self.df is None:
            return []
        
        result = self.df[self.df['Status'].str.lower() == status.lower()]
        return result.to_dict('records')
    
    def get_by_genre(self, genre: str) -> List[Dict]:
        """Get series/film berdasarkan genre"""
        if self.df is None:
            return []
        
        result = self.df[self.df['Genre'].str.contains(genre, case=False, na=False)]
        return result.to_dict('records')
    
    def get_statistics(self) -> Dict:
        """Get statistik dari watchlist"""
        if self.df is None:
            return {}
        
        stats = {
            'total': len(self.df),
            'watching': len(self.df[self.df['Status'].str.lower() == 'watching']),
            'completed': len(self.df[self.df['Status'].str.lower() == 'completed']),
            'dropped': len(self.df[self.df['Status'].str.lower() == 'dropped']),
            'avg_rating': round(pd.to_numeric(self.df['Rating'], errors='coerce').mean(), 2)
        }
        return stats
    
    def format_item(self, item: Dict) -> str:
        """Format item untuk ditampilkan di Telegram"""
        try:
            return (
                f"📺 <b>{item.get('Judul', 'N/A')}</b>\n"
                f"📂 Genre: {item.get('Genre', 'N/A')}\n"
                f"🔄 Status: {item.get('Status', 'N/A')}\n"
                f"⭐ Rating: {item.get('Rating', 'N/A')}/10\n"
                f"📍 Episode: {item.get('Episode', 'N/A')}\n"
                f"📅 Ditambah: {item.get('Tanggal Ditambah', 'N/A')}\n"
                f"📝 Catatan: {item.get('Catatan', '-')}"
            )
        except Exception as e:
            logger.error(f"Error formatting item: {e}")
            return "Error formatting item"
    
    def refresh(self) -> bool:
        """Refresh data dari Google Sheets"""
        return self.load_data()
