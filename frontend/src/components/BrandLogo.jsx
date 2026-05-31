import logoUrl from '../assets/lostfound-logo.svg';
import { cn } from '../utils/cn';

export default function BrandLogo({ className = '', imageClassName = '' }) {
  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-2xl bg-white border border-ipb-green/10 shadow-lg shadow-ipb-green/15 overflow-hidden',
        className
      )}
    >
      <img src={logoUrl} alt="Lost & Found IPB" className={cn('h-[78%] w-[78%] object-contain', imageClassName)} />
    </div>
  );
}
