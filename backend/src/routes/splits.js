// src/routes/splits.js
import express from 'express';
import { verifyToken } from '../middlewares/auth.js';
import { splitTransaction, getDebtSummary } from '../controllers/splitController.js';

const router = express.Router();
router.use(verifyToken);

router.post('/', splitTransaction);    // POST /api/splits (Create a split)
router.get('/summary', getDebtSummary); // GET /api/splits/summary (Dashboard)

export default router;