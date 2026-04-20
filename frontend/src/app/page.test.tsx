import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import HomePage from './page';

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
})) as any;

// Mock WebGL context for canvas elements
HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
  fillRect: vi.fn(),
  clearRect: vi.fn(),
  getImageData: vi.fn(() => ({
    data: new Array(4),
  })),
  putImageData: vi.fn(),
  createImageData: vi.fn(() => []),
  setTransform: vi.fn(),
  drawImage: vi.fn(),
  save: vi.fn(),
  fillText: vi.fn(),
  restore: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  closePath: vi.fn(),
  stroke: vi.fn(),
  translate: vi.fn(),
  scale: vi.fn(),
  rotate: vi.fn(),
  arc: vi.fn(),
  fill: vi.fn(),
  measureText: vi.fn(() => ({ width: 0 })),
  transform: vi.fn(),
  rect: vi.fn(),
  clip: vi.fn(),
})) as any;

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    pathname: '/',
  })),
  useSearchParams: vi.fn(() => new URLSearchParams()),
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href }: any) => <a href={href}>{children}</a>,
}));

// Mock Three.js based components that require WebGL
vi.mock('@/components/landing2/Murmuration', () => ({
  default: () => <div data-testid="murmuration">Murmuration</div>,
}));

vi.mock('@/components/landing2/SectionReveal', () => ({
  default: ({ children }: any) => <div data-testid="section-reveal">{children}</div>,
}));

describe('HomePage', () => {
  it('should render without crashing', () => {
    render(<HomePage />);
    expect(document.body).toBeTruthy();
  });

  it('should render page content', () => {
    const { container } = render(<HomePage />);
    expect(container).toBeTruthy();
  });

  it('should not throw errors during render', () => {
    expect(() => {
      render(<HomePage />);
    }).not.toThrow();
  });
});
