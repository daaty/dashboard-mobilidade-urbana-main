import { useState } from 'react';

export const useDriverModal = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedDriverId, setSelectedDriverId] = useState(null);
  const [selectedDriverName, setSelectedDriverName] = useState('');

  const openModal = (driverId, driverName) => {
    setSelectedDriverId(driverId);
    setSelectedDriverName(driverName);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedDriverId(null);
    setSelectedDriverName('');
  };

  return {
    isModalOpen,
    selectedDriverId,
    selectedDriverName,
    openModal,
    closeModal
  };
};
