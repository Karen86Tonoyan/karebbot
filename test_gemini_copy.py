#!/usr/bin/env python3
"""
ALFA CORE - Gemini Copy Test Script
Operation Dawn - Quick Verification

Tests:
1. Import all components
2. Initialize CoreManager
3. Health check
4. Test dispatch (if GEMINI_API_KEY is set)
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

LOG = logging.getLogger(__name__)

def test_imports():
    """Test 1: Import all ALFA Core components"""
    LOG.info("=" * 60)
    LOG.info("TEST 1: Importing ALFA Core components")
    LOG.info("=" * 60)

    try:
        from alfa_core import (
            CoreManager,
            get_core_manager,
            ProviderRegistry,
            GeminiProvider,
            MirrorEngine,
            Cerber,
            SecurityException
        )
        LOG.info("✅ All imports successful")
        return True
    except Exception as e:
        LOG.error(f"❌ Import failed: {e}")
        return False


def test_initialization():
    """Test 2: Initialize CoreManager"""
    LOG.info("\n" + "=" * 60)
    LOG.info("TEST 2: Initializing CoreManager")
    LOG.info("=" * 60)

    try:
        from alfa_core import get_core_manager

        manager = get_core_manager()
        LOG.info(f"✅ CoreManager initialized")
        LOG.info(f"   Providers: {manager.registry.list()}")

        return True, manager
    except Exception as e:
        LOG.error(f"❌ Initialization failed: {e}")
        return False, None


def test_health_check(manager):
    """Test 3: Health check"""
    LOG.info("\n" + "=" * 60)
    LOG.info("TEST 3: Health Check")
    LOG.info("=" * 60)

    try:
        health = manager.health_check()
        LOG.info("✅ Health check passed")
        LOG.info(f"   Status: {health['status']}")
        LOG.info(f"   Components: {list(health['components'].keys())}")

        # Check each component
        for comp_name, comp_data in health['components'].items():
            status = comp_data.get('status', 'unknown')
            LOG.info(f"   - {comp_name}: {status}")

        return True
    except Exception as e:
        LOG.error(f"❌ Health check failed: {e}")
        return False


def test_dispatch(manager):
    """Test 4: Test dispatch (requires GEMINI_API_KEY)"""
    LOG.info("\n" + "=" * 60)
    LOG.info("TEST 4: Dispatch Test")
    LOG.info("=" * 60)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        LOG.warning("⚠️  GEMINI_API_KEY not set - skipping dispatch test")
        LOG.info("   Set GEMINI_API_KEY environment variable to enable this test")
        return True  # Not a failure, just skipped

    try:
        LOG.info("Testing Gemini dispatch with test prompt...")

        result = manager.dispatch(
            prompt="Hello! This is a test from ALFA Core. Please respond with 'ALFA Core operational.'",
            provider_name="gemini"
        )

        LOG.info("✅ Dispatch successful")
        LOG.info(f"   Session ID: {result.get('session_id')}")
        LOG.info(f"   Provider: {result.get('provider')}")
        LOG.info(f"   Model: {result.get('model')}")
        LOG.info(f"   Tokens: {result.get('tokens')}")
        LOG.info(f"   Response (first 100 chars): {result.get('text', '')[:100]}...")

        # Test retrieval
        session_id = result.get('session_id')
        if session_id:
            LOG.info("\n   Testing session retrieval...")
            session = manager.get_session(session_id)
            if session:
                LOG.info(f"   ✅ Session retrieved from Mirror")
            else:
                LOG.warning(f"   ⚠️  Session retrieval failed")

        return True
    except Exception as e:
        LOG.error(f"❌ Dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mirror_stats(manager):
    """Test 5: Mirror Engine stats"""
    LOG.info("\n" + "=" * 60)
    LOG.info("TEST 5: Mirror Engine Stats")
    LOG.info("=" * 60)

    try:
        stats = manager.stats()
        mirror_stats = stats.get('mirror', {})

        LOG.info("✅ Mirror stats retrieved")
        LOG.info(f"   Sessions: {mirror_stats.get('sessions', 0)}")
        LOG.info(f"   Media files: {mirror_stats.get('media_files', 0)}")
        LOG.info(f"   Storage: {mirror_stats.get('storage_mb', 0)} MB")
        LOG.info(f"   Path: {mirror_stats.get('storage_path', 'unknown')}")

        return True
    except Exception as e:
        LOG.error(f"❌ Mirror stats failed: {e}")
        return False


def main():
    """Run all tests"""
    LOG.info("\n")
    LOG.info("╔═══════════════════════════════════════════════════════════╗")
    LOG.info("║         ALFA CORE - GEMINI COPY TEST SUITE               ║")
    LOG.info("║              Operation Dawn Verification                  ║")
    LOG.info("╚═══════════════════════════════════════════════════════════╝")
    LOG.info("\n")

    results = []
    manager = None

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Initialization
    success, manager = test_initialization()
    results.append(("Initialization", success))

    if manager:
        # Test 3: Health Check
        results.append(("Health Check", test_health_check(manager)))

        # Test 4: Dispatch
        results.append(("Dispatch", test_dispatch(manager)))

        # Test 5: Mirror Stats
        results.append(("Mirror Stats", test_mirror_stats(manager)))

    # Summary
    LOG.info("\n" + "=" * 60)
    LOG.info("TEST SUMMARY")
    LOG.info("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        LOG.info(f"{status} - {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    LOG.info("=" * 60)
    LOG.info(f"TOTAL: {passed}/{total} tests passed")
    LOG.info("=" * 60)

    if passed == total:
        LOG.info("\n🎉 All tests passed! ALFA Core is operational.")
        LOG.info("\nNext steps:")
        LOG.info("  1. Set GEMINI_API_KEY environment variable")
        LOG.info("  2. Run: python app.py")
        LOG.info("  3. Test endpoint: POST http://localhost:8000/api/v1/gemini")
        return 0
    else:
        LOG.error("\n❌ Some tests failed. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
