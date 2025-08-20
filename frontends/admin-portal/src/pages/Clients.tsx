import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api';

interface Client {
  id: string;
  name: string;
  child: string;
}

const fetchClients = async () => {
  const res = await api.get('/v1/admin/clients');
  return res.data.clients as Client[];
};

const Clients: React.FC = () => {
  const { data, isLoading, error } = useQuery(['clients'], fetchClients);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading clients</div>;

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-2">Clients</h1>
      <table className="min-w-full border">
        <thead>
          <tr>
            <th className="border px-2 py-1">Parent</th>
            <th className="border px-2 py-1">Child</th>
          </tr>
        </thead>
        <tbody>
          {data?.map((c) => (
            <tr key={c.id}>
              <td className="border px-2 py-1">{c.name}</td>
              <td className="border px-2 py-1">{c.child}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Clients;
