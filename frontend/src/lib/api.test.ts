/* Comprehensive tests for API client. */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock Supabase before importing API functions
vi.mock('@/lib/supabase/client', () => ({
  createClient: vi.fn(() => ({
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: { access_token: 'test-token' } },
      }),
    },
  })),
}));

import {
  createBusiness,
  updateBusiness,
  listBusinesses,
  createSimulation,
  getSimulationProgress,
  getSimulationResult,
  submitRealOutcome,
  getAccuracyStats,
  listSimulations,
} from './api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Business API', () => {
    it('should create a business', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '123', name: 'Test Business' }),
      });

      const result = await createBusiness({
        name: 'Test Business',
        type: 'retail',
        description: 'A test business',
        customer_description: 'Test customers',
        location: 'Test City',
      });

      expect(mockFetch).toHaveBeenCalled();
      expect(result).toBeDefined();
    });

    it('should update a business', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '123', name: 'Updated' }),
      });

      const result = await updateBusiness('123', {
        name: 'Updated',
        type: 'retail',
        description: 'Updated description',
        customer_description: 'Updated customers',
        location: 'Updated City',
      });

      expect(mockFetch).toHaveBeenCalled();
      expect(result).toBeDefined();
    });

    it('should list businesses', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { id: '1', name: 'Business 1' },
          { id: '2', name: 'Business 2' },
        ],
      });

      const result = await listBusinesses();

      expect(mockFetch).toHaveBeenCalled();
      expect(Array.isArray(result)).toBeTruthy();
    });
  });

  describe('Simulation API', () => {
    it('should create a simulation', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'sim-123', status: 'running' }),
      });

      const result = await createSimulation({
        business_id: 'business-123',
        question: 'What if we raised prices?',
        variant_a: 'Current',
        variant_b: 'New',
      });

      expect(mockFetch).toHaveBeenCalled();
      expect(result).toBeDefined();
    });

    it('should get simulation progress', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'running',
          step: 'Generating personas',
          step_index: 1,
          total_steps: 3,
          personas_generated: 5,
          personas_total: 12,
        }),
      });

      const result = await getSimulationProgress('sim-123');

      expect(mockFetch).toHaveBeenCalled();
      expect(result).toBeDefined();
    });

    it('should get simulation result', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 'sim-123',
          status: 'completed',
          summary: 'Customers would be mixed',
        }),
      });

      const result = await getSimulationResult('sim-123');

      expect(mockFetch).toHaveBeenCalled();
      expect(result).toBeDefined();
    });

    it('should list simulations', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { id: 'sim-1', question: 'Q1' },
          { id: 'sim-2', question: 'Q2' },
        ],
      });

      const result = await listSimulations();

      expect(mockFetch).toHaveBeenCalled();
      expect(Array.isArray(result)).toBeTruthy();
    });
  });

  describe('Outcome Submission', () => {
    it('should submit a real outcome', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'outcome-123' }),
      });

      const result = await submitRealOutcome('sim-123', {
        what_actually_happened: 'Sales increased 5%',
      });

      expect(mockFetch).toHaveBeenCalled();
      expect(result).toBeDefined();
    });
  });

  describe('Accuracy Stats', () => {
    it('should get accuracy statistics', async () => {
      const mockFetch = global.fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ accuracy_pct: 67.5, total_outcomes: 4 }),
      });

      const result = await getAccuracyStats();

      expect(mockFetch).toHaveBeenCalled();
      expect(result).toBeDefined();
    });
  });
});
