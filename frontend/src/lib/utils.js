// Função utilitária para concatenar classes condicionalmente
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}
