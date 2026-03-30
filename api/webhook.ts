import { VercelRequest, VercelResponse } from '@vercel/node';
import { bot } from '../src/bot';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  try {
    await bot.handleUpdate(req.body, res);
    res.status(200).send('OK');
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).send('Internal Server Error');
  }
}
