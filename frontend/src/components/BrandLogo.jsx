import logoUrl from '../assets/lostfound-logo.svg';
import { cn } from '../utils/cn';

export default function BrandLogo({ className = '', imageClassName = '' }) {
  return (
    <div className={cn('flex items-center justify-center overflow-visible', className)}>
      <img src={logoUrl} alt="Lost & Found IPB" className={cn('h-full w-full object-contain', imageClassName)} />
    </div>
  );
}
