import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('@/lib/supabase/client', () => ({
  createClient: vi.fn(() => ({
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: { access_token: 'test-token' } },
      }),
    },
  })),
}));

global.fetch = vi.fn();

import FileUploadZone from './FileUploadZone';

describe('FileUploadZone', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render upload zone for customers', () => {
      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      expect(screen.getByText(/Activate John's digital twin/i)).toBeInTheDocument();
    });

    it('should render upload zone for vendors', () => {
      render(
        <FileUploadZone
          contactId="vendor-123"
          contactType="vendor"
          contactName="Acme Corp"
        />
      );

      expect(screen.getByText(/Activate Acme Corp's digital twin/i)).toBeInTheDocument();
    });

    it('should display drop zone', () => {
      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      expect(screen.getByText(/Drop files here or click to upload/i)).toBeInTheDocument();
    });

    it('should display privacy notice', () => {
      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      expect(screen.getByText(/All files are anonymised immediately/i)).toBeInTheDocument();
    });
  });

  describe('Customer Sources', () => {
    it('should display customer upload sources', () => {
      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      expect(screen.getByText(/WhatsApp conversation/i)).toBeInTheDocument();
      expect(screen.getByText(/Email thread/i)).toBeInTheDocument();
    });
  });

  describe('Vendor Sources', () => {
    it('should display vendor upload sources', () => {
      render(
        <FileUploadZone
          contactId="vendor-123"
          contactType="vendor"
          contactName="Supplier"
        />
      );

      expect(screen.getByText(/WhatsApp conversations/i)).toBeInTheDocument();
      expect(screen.getByText(/Email threads/i)).toBeInTheDocument();
    });
  });

  describe('File Upload', () => {
    it('should show success message after upload', async () => {
      const user = userEvent.setup();
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          message_count: 25,
          twin_confidence: 'high',
        }),
      });

      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      const dropZone = screen.getByText(/Drop files here/i).closest('label');
      const input = dropZone?.querySelector('input[type="file"]') as HTMLInputElement;

      const file = new File(['data'], 'file.txt', { type: 'text/plain' });
      await user.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText(/Upload successful/i)).toBeInTheDocument();
      });
    });

    it('should call onUploadComplete callback', async () => {
      const user = userEvent.setup();
      const onComplete = vi.fn();

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          message_count: 15,
          twin_confidence: 'medium',
        }),
      });

      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
          onUploadComplete={onComplete}
        />
      );

      const dropZone = screen.getByText(/Drop files here/i).closest('label');
      const input = dropZone?.querySelector('input[type="file"]') as HTMLInputElement;

      const file = new File(['data'], 'file.txt', { type: 'text/plain' });
      await user.upload(input, file);

      await waitFor(() => {
        expect(onComplete).toHaveBeenCalled();
      });
    });

    it('should handle upload failure', async () => {
      const user = userEvent.setup();
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        text: async () => 'File format not supported',
      });

      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      const dropZone = screen.getByText(/Drop files here/i).closest('label');
      const input = dropZone?.querySelector('input[type="file"]') as HTMLInputElement;

      const file = new File(['data'], 'file.txt');
      await user.upload(input, file);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalled();
      });

      alertSpy.mockRestore();
    });

    it('should handle network errors', async () => {
      const user = userEvent.setup();
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      const dropZone = screen.getByText(/Drop files here/i).closest('label');
      const input = dropZone?.querySelector('input[type="file"]') as HTMLInputElement;

      const file = new File(['data'], 'file.txt');
      await user.upload(input, file);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Upload failed');
      });

      alertSpy.mockRestore();
    });
  });

  describe('File Type Validation', () => {
    it('should accept text files', () => {
      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      const dropZone = screen.getByText(/Drop files here/i).closest('label');
      const input = dropZone?.querySelector('input[type="file"]') as HTMLInputElement;

      expect(input?.accept).toContain('.txt');
    });

    it('should accept pdf files', () => {
      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="John"
        />
      );

      const dropZone = screen.getByText(/Drop files here/i).closest('label');
      const input = dropZone?.querySelector('input[type="file"]') as HTMLInputElement;

      expect(input?.accept).toContain('.pdf');
    });
  });

  describe('Edge Cases', () => {
    it('should handle long contact names', () => {
      const longName = 'A'.repeat(100);
      const { container } = render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName={longName}
        />
      );

      expect(container).toBeTruthy();
    });

    it('should render with special characters in name', () => {
      render(
        <FileUploadZone
          contactId="cust-123"
          contactType="customer"
          contactName="O'Brien & Sons"
        />
      );

      expect(screen.getByText(/Activate O'Brien & Sons's digital twin/i)).toBeInTheDocument();
    });
  });
});
