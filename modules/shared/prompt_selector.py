#!/usr/bin/env python3
"""
Prompt Selection Module

Handles random prompt selection from the prompts JSON file with usage tracking.
"""

import json
import random
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PromptSelector:
    """Manages prompt selection and usage tracking."""
    
    def __init__(self, prompts_file: str = None, usage_file: str = None):
        """
        Initialize the prompt selector.
        
        Args:
            prompts_file: Path to the prompts JSON file
            usage_file: Path to the usage tracking file
        """
        # Default paths relative to project root
        if prompts_file is None:
            prompts_file = os.path.join(os.path.dirname(__file__), '../../prompts/analysis_prompts_2025_09_19.json')
        
        if usage_file is None:
            usage_file = os.path.join(os.path.dirname(__file__), '../../prompts/prompt_usage.json')
        
        self.prompts_file = Path(prompts_file)
        self.usage_file = Path(usage_file)
        self.prompts_data = None
        self.usage_data = None
        
        # Load data
        self._load_prompts()
        self._load_usage_data()
    
    def _load_prompts(self):
        """Load prompts from JSON file."""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                self.prompts_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in prompts file: {e}")
    
    def _load_usage_data(self):
        """Load usage tracking data."""
        try:
            if self.usage_file.exists():
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    self.usage_data = json.load(f)
            else:
                # Initialize usage data structure
                self.usage_data = {
                    "used_prompts": [],
                    "usage_history": [],
                    "last_reset": None,
                    "total_runs": 0
                }
                self._save_usage_data()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in usage file: {e}")
    
    def _save_usage_data(self):
        """Save usage tracking data to file."""
        try:
            # Ensure directory exists
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save usage data: {e}")
    
    def get_available_prompts(self) -> List[Dict]:
        """Get list of prompts that haven't been used yet."""
        used_ids = set(self.usage_data.get("used_prompts", []))
        available_prompts = [
            prompt for prompt in self.prompts_data["prompts"]
            if prompt["id"] not in used_ids
        ]
        return available_prompts
    
    def get_random_prompt(self, category_filter: Optional[str] = None, 
                         difficulty_filter: Optional[str] = None) -> Optional[Dict]:
        """
        Get a random prompt from available prompts.
        
        Args:
            category_filter: Filter by category name
            difficulty_filter: Filter by difficulty level ('intermediate' or 'advanced')
            
        Returns:
            Random prompt dict or None if no prompts available
        """
        available_prompts = self.get_available_prompts()
        
        # Apply filters
        if category_filter:
            available_prompts = [
                p for p in available_prompts 
                if p.get("category", "").lower() == category_filter.lower()
            ]
        
        if difficulty_filter:
            available_prompts = [
                p for p in available_prompts 
                if p.get("difficulty", "").lower() == difficulty_filter.lower()
            ]
        
        if not available_prompts:
            return None
        
        return random.choice(available_prompts)
    
    def mark_prompt_used(self, prompt_id: int) -> bool:
        """
        Mark a prompt as used.
        
        Args:
            prompt_id: ID of the prompt to mark as used
            
        Returns:
            True if successfully marked, False if already used
        """
        if prompt_id in self.usage_data.get("used_prompts", []):
            return False
        
        # Add to used prompts
        if "used_prompts" not in self.usage_data:
            self.usage_data["used_prompts"] = []
        self.usage_data["used_prompts"].append(prompt_id)
        
        # Add to usage history
        if "usage_history" not in self.usage_data:
            self.usage_data["usage_history"] = []
        
        usage_entry = {
            "prompt_id": prompt_id,
            "used_at": datetime.now().isoformat(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Find the prompt details
        prompt_details = next(
            (p for p in self.prompts_data["prompts"] if p["id"] == prompt_id),
            None
        )
        
        if prompt_details:
            usage_entry.update({
                "category": prompt_details.get("category"),
                "difficulty": prompt_details.get("difficulty"),
                "prompt_text": prompt_details.get("prompt")
            })
        
        self.usage_data["usage_history"].append(usage_entry)
        
        # Update total runs
        self.usage_data["total_runs"] = self.usage_data.get("total_runs", 0) + 1
        
        # Save the updated data
        self._save_usage_data()
        return True
    
    def select_and_mark_prompt(self, category_filter: Optional[str] = None,
                              difficulty_filter: Optional[str] = None) -> Optional[Dict]:
        """
        Select a random prompt and mark it as used.
        
        Args:
            category_filter: Filter by category name
            difficulty_filter: Filter by difficulty level
            
        Returns:
            Selected prompt dict or None if no prompts available
        """
        selected_prompt = self.get_random_prompt(category_filter, difficulty_filter)
        
        if selected_prompt:
            success = self.mark_prompt_used(selected_prompt["id"])
            if success:
                return selected_prompt
        
        return None
    
    def reset_usage(self, confirm: bool = False) -> bool:
        """
        Reset usage tracking (mark all prompts as unused).
        
        Args:
            confirm: Must be True to actually reset
            
        Returns:
            True if reset successfully
        """
        if not confirm:
            return False
        
        self.usage_data["used_prompts"] = []
        self.usage_data["last_reset"] = datetime.now().isoformat()
        self._save_usage_data()
        return True
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics."""
        total_prompts = len(self.prompts_data["prompts"])
        used_prompts = len(self.usage_data.get("used_prompts", []))
        available_prompts = total_prompts - used_prompts
        
        return {
            "total_prompts": total_prompts,
            "used_prompts": used_prompts,
            "available_prompts": available_prompts,
            "usage_percentage": (used_prompts / total_prompts * 100) if total_prompts > 0 else 0,
            "total_runs": self.usage_data.get("total_runs", 0),
            "last_reset": self.usage_data.get("last_reset"),
            "categories_available": list(set(
                p["category"] for p in self.get_available_prompts()
            )),
            "difficulty_levels_available": list(set(
                p["difficulty"] for p in self.get_available_prompts()
            ))
        }
    
    def get_prompt_by_id(self, prompt_id: int) -> Optional[Dict]:
        """Get a specific prompt by ID."""
        return next(
            (p for p in self.prompts_data["prompts"] if p["id"] == prompt_id),
            None
        )
    
    def is_prompt_available(self, prompt_id: int) -> bool:
        """Check if a prompt is available (not used)."""
        return prompt_id not in self.usage_data.get("used_prompts", [])


def main():
    """CLI interface for prompt selection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Prompt Selection CLI")
    parser.add_argument("--select", action="store_true", help="Select and mark a random prompt")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--difficulty", type=str, choices=["intermediate", "advanced"], 
                       help="Filter by difficulty")
    parser.add_argument("--stats", action="store_true", help="Show usage statistics")
    parser.add_argument("--reset", action="store_true", help="Reset usage tracking")
    parser.add_argument("--list-available", action="store_true", help="List available prompts")
    
    args = parser.parse_args()
    
    try:
        selector = PromptSelector()
        
        if args.stats:
            stats = selector.get_usage_stats()
            print("\n📊 Prompt Usage Statistics")
            print("=" * 40)
            print(f"Total Prompts: {stats['total_prompts']}")
            print(f"Used Prompts: {stats['used_prompts']}")
            print(f"Available Prompts: {stats['available_prompts']}")
            print(f"Usage Percentage: {stats['usage_percentage']:.1f}%")
            print(f"Total Runs: {stats['total_runs']}")
            if stats['last_reset']:
                print(f"Last Reset: {stats['last_reset']}")
            print(f"\nAvailable Categories: {', '.join(stats['categories_available'])}")
            print(f"Available Difficulties: {', '.join(stats['difficulty_levels_available'])}")
        
        elif args.reset:
            confirm = input("Are you sure you want to reset usage tracking? (yes/no): ")
            if confirm.lower() in ['yes', 'y']:
                if selector.reset_usage(confirm=True):
                    print("✅ Usage tracking reset successfully!")
                else:
                    print("❌ Failed to reset usage tracking")
            else:
                print("Reset cancelled")
        
        elif args.list_available:
            available = selector.get_available_prompts()
            print(f"\n📝 Available Prompts ({len(available)})")
            print("=" * 50)
            for prompt in available:
                print(f"ID: {prompt['id']} | {prompt['category']} | {prompt['difficulty']}")
                print(f"Prompt: {prompt['prompt'][:100]}...")
                print("-" * 50)
        
        elif args.select:
            selected = selector.select_and_mark_prompt(
                category_filter=args.category,
                difficulty_filter=args.difficulty
            )
            
            if selected:
                print("\n🎯 Selected Prompt:")
                print("=" * 50)
                print(f"ID: {selected['id']}")
                print(f"Category: {selected['category']}")
                print(f"Difficulty: {selected['difficulty']}")
                print(f"Expected Charts: {', '.join(selected['expected_charts'])}")
                print(f"\nPrompt: {selected['prompt']}")
                print("\n✅ Prompt marked as used!")
            else:
                print("❌ No available prompts found with the specified criteria")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
