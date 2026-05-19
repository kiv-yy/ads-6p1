export function normalizeItemType(type) {
  const value = String(type || '').toLowerCase();
  if (value === 'lost' || value === 'kehilangan') return 'LOST';
  if (value === 'found' || value === 'temuan') return 'FOUND';
  return value.toUpperCase();
}

export function isLostItem(type) {
  return normalizeItemType(type) === 'LOST';
}

export function itemTypeLabel(type) {
  return isLostItem(type) ? 'Hilang' : 'Ditemukan';
}

export function itemTypeVariant(type) {
  return isLostItem(type) ? 'hilang' : 'ditemukan';
}
