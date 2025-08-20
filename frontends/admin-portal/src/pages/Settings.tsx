import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api';

interface SettingsData {
  dropInRSD: number;
  pass4RSD: number;
  pass8RSD: number;
  cooldownSec: number;
  bookingEnabled: boolean;
}

const fetchSettings = async () => {
  const res = await api.get('/v1/admin/settings');
  return res.data as SettingsData;
};

const Settings: React.FC = () => {
  const queryClient = useQueryClient();
  const { data } = useQuery(['settings'], fetchSettings);

  const mutation = useMutation(
    (values: SettingsData) => api.patch('/v1/admin/settings', values),
    {
      onSuccess: () => queryClient.invalidateQueries(['settings']),
    }
  );

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);
    const values: SettingsData = {
      dropInRSD: Number(formData.get('dropInRSD')),
      pass4RSD: Number(formData.get('pass4RSD')),
      pass8RSD: Number(formData.get('pass8RSD')),
      cooldownSec: Number(formData.get('cooldownSec')),
      bookingEnabled: formData.get('bookingEnabled') === 'on',
    };
    mutation.mutate(values);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-2">Settings</h1>
      {data && (
        <form onSubmit={onSubmit} className="space-y-2 max-w-sm">
          <label className="block">
            <span>Drop-in price</span>
            <input
              name="dropInRSD"
              type="number"
              defaultValue={data.dropInRSD}
              className="border p-1 w-full"
            />
          </label>
          <label className="block">
            <span>Pass 4 price</span>
            <input
              name="pass4RSD"
              type="number"
              defaultValue={data.pass4RSD}
              className="border p-1 w-full"
            />
          </label>
          <label className="block">
            <span>Pass 8 price</span>
            <input
              name="pass8RSD"
              type="number"
              defaultValue={data.pass8RSD}
              className="border p-1 w-full"
            />
          </label>
          <label className="block">
            <span>Cooldown sec</span>
            <input
              name="cooldownSec"
              type="number"
              defaultValue={data.cooldownSec}
              className="border p-1 w-full"
            />
          </label>
          <label className="block">
            <span>Booking enabled</span>
            <input
              name="bookingEnabled"
              type="checkbox"
              defaultChecked={data.bookingEnabled}
              className="ml-2"
            />
          </label>
          <button type="submit" className="px-4 py-1 border">Save</button>
        </form>
      )}
    </div>
  );
};

export default Settings;
