"use client";

import { useState, useEffect } from "react";

/**
 * Hook customizado para gerenciar estado sincronizado com o localStorage.
 * Resolve problemas de hidratação do Next.js e sincroniza o valor entre guias
 * (tabs) e diferentes componentes na mesma página.
 *
 * @param key - A chave que será usada para salvar o valor no localStorage.
 * @param initialValue - O valor inicial caso não exista nada salvo.
 * @returns Um array contendo o valor atual e uma função para atualizá-lo.
 */
export function useLocalStorage<T>(key: string, initialValue: T) {
  // Passamos o valor inicial diretamente para evitar erro de hidratação
  // entre o servidor e o cliente no React 18+ / Next.js.
  const [storedValue, setStoredValue] = useState<T>(initialValue);
  const [isHydrated, setIsHydrated] = useState(false);

  // Efeito executado apenas no lado do cliente (após montagem) para resgatar
  // o valor real salvo no localStorage e atualizar o estado, se existir.
  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const item = window.localStorage.getItem(key);
        if (item) {
          setStoredValue(JSON.parse(item));
        }
      } catch (error) {
        console.warn(`Erro ao ler a chave "${key}" do localStorage:`, error);
      }
      setIsHydrated(true);
    }
  }, [key]);

  // Função para atualizar o valor, com a mesma API do useState (aceita callback).
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      if (typeof window !== "undefined") {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }

      // Dispara um evento customizado para que outros componentes que usam o hook 
      // nesta mesma aba do navegador saibam que o valor mudou e se atualizem.
      window.dispatchEvent(new Event("local-storage-sync"));
    } catch (error) {
      console.warn(`Erro ao salvar a chave "${key}" no localStorage:`, error);
    }
  };

  // Efeito responsável por ouvir mudanças de outros lugares e atualizar localmente.
  // Escuta tanto a mudança em outras abas ("storage") quanto nesta mesma ("local-storage-sync").
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent | Event) => {
      try {
        if (typeof window !== "undefined") {
          const item = window.localStorage.getItem(key);
          if (item) {
            setStoredValue(JSON.parse(item));
          }
        }
      } catch (error) {
        console.warn(`Erro na sincronização do storage:`, error);
      }
    };

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("local-storage-sync", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("local-storage-sync", handleStorageChange);
    };
  }, [key]);

  return [storedValue, setValue, isHydrated] as const;
}
