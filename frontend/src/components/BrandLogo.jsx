import logoGreen from '../assets/logo-green.png';
import logoWhite from '../assets/logo-white.png';
import { cn } from '../utils/cn';

export default function BrandLogo({ className = '', imageClassName = '', variant = 'green' }) {
  const logoUrl = variant === 'white' ? logoWhite : logoGreen;

  return (
    <div className={cn('flex items-center justify-center overflow-visible', className)}>
      <img src={logoUrl} alt="Lost & Found IPB" className={cn('h-full w-full object-contain', imageClassName)} />
    </div>
  );
}
