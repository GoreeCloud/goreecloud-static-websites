#!/usr/bin/env python3
from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[1]
class OfficialArtworkTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.index=(ROOT/'index.html').read_text(encoding='utf-8')
    cls.manifest=json.loads((ROOT/'docs/visual-identity-sources.json').read_text(encoding='utf-8'))
  def test_placeholders_are_removed(self):
    for marker in ('class="service-icon"','platform-native-mark','social-letter','neutral Glaze UI letter marks instead of third-party logo artwork'):
      self.assertNotIn(marker,self.index)
  def test_canonical_goreecloud_logo_is_visible(self):
    self.assertGreaterEqual(self.index.count('assets/goreecloud-logo.svg'),3)
  def test_only_text_fallback_when_artwork_missing(self):
    for r in self.manifest['assets']:
      if r.get('official_artwork_exists') is False: self.assertEqual(r.get('fallback'),'text-only')
  def test_social_cards_use_local_official_identity_files(self):
    for name in ('instagram','pinterest','threads','tiktok','youtube','x','reddit','github'):
      self.assertIn(f'assets/social/{name}.ico',self.index)
if __name__=='__main__': unittest.main()
