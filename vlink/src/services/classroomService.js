import { USE_MOCK, API_BASE_URL } from './config';
import db from '../mock/db.json';
import { v4 as uuidv4 } from 'uuid';

export const createClass = async (title) => {
  if (USE_MOCK) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newClass = {
          id: uuidv4(),
          title,
          teacher: "You",
          code: Math.random().toString(36).substring(2, 8).toUpperCase(),
          status: 'live',
          participants: 0
        };
        // In a real app, you'd push this to the db variable or state
        console.log("Mock Class Created:", newClass);
        resolve(newClass);
      }, 500);
    });
  } else {
    const res = await fetch(`${API_BASE_URL}/classes/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    return res.json();
  }
};

export const joinClass = async (code) => {
  if (USE_MOCK) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const foundClass = db.classes.find(c => c.code === code);
        if (foundClass) resolve({ success: true, classId: foundClass.id });
        else reject({ success: false, message: "Invalid Class Code" });
      }, 500);
    });
  } else {
    const res = await fetch(`${API_BASE_URL}/classes/join`, {
      method: 'POST',
      body: JSON.stringify({ code })
    });
    return res.json();
  }
};