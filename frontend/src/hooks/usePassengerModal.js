import { useState } from 'react';

export const usePassengerModal = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPassengerId, setSelectedPassengerId] = useState(null);
  const [selectedPassengerName, setSelectedPassengerName] = useState('');

  const openModal = (passengerId, passengerName) => {
    setSelectedPassengerId(passengerId);
    setSelectedPassengerName(passengerName);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedPassengerId(null);
    setSelectedPassengerName('');
  };

  return {
    isModalOpen,
    selectedPassengerId,
    selectedPassengerName,
    openModal,
    closeModal
  };
};