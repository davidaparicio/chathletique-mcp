import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from stravalib.client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('STRAVA_ACCESS_TOKEN')
if not token:
    print("Error: STRAVA_ACCESS_TOKEN not found in .env file")
    exit(1)

client = Client(access_token=token)

def figures_speed_hr_by_activity(
    client,
    number_of_activity: int,
    resolution: str = "high",
    series_type: str = "time",
    *,
    # Paramètres “protocole MCP”
    resample_hz: float = 1.0,          # grille uniforme (1 Hz)
    smooth_win_s: float = 5.0,         # lissage moyenne glissante (secondes)
    min_speed_kmh: float = 0.5,        # seuil pause (speed < min = pause)
    winsor_pct: float = 0.5,           # découpe extrêmes (0.5%/0.5%)
    clip_hr_range: tuple | None = (30, 220),  # bornage physiologique FC
    clip_speed_range: tuple | None = (0, 50), # bornage vitesse
):
    """
    Retourne une liste de tuples: [(activity_name, fig_hr, fig_speed), ...]
    - fig_hr : courbe FC (rouge) en fonction du temps (s) — flux nettoyé, 1 Hz
    - fig_speed : courbe vitesse (bleue) en fonction du temps (s) — flux nettoyé, 1 Hz
    Figures séparées, prêtes pour un protocole MCP.
    """
    def _winsorize(x, pct=0.5):
        if x is None or len(x) == 0:
            return x
        lo = np.nanpercentile(x, pct)
        hi = np.nanpercentile(x, 100 - pct)
        return np.clip(x, lo, hi)

    def _moving_avg(x, win_samples: int):
        if x is None or len(x) == 0 or win_samples <= 1:
            return x
        # Convolution “valid” avec bordures conservées via mode='same'
        kernel = np.ones(win_samples, dtype=float) / win_samples
        y = np.convolve(x, kernel, mode="same")
        return y

    def _resample_to_uniform_time(t, *arrays, hz=1.0):
        """
        Interpole sur une grille uniforme [0, T] à pas 1/hz.
        Renvoie t_new, arrays_interpolés (NaN-safe).
        """
        if t is None or len(t) < 2:
            return t, arrays
        t = np.asarray(t, dtype=float)
        t = t - t[0]  # origine à 0
        T = float(t[-1])
        if T <= 0:
            return t, arrays
        step = 1.0 / float(hz)
        t_new = np.arange(0.0, T + 1e-9, step, dtype=float)
        out = []
        for a in arrays:
            if a is None or len(a) != len(t):
                out.append(None)
                continue
            a = np.asarray(a, dtype=float)
            # Interpolation linéaire; si NaN, on remplace par interpolation des points valides
            mask = ~np.isnan(a)
            if mask.sum() < 2:
                out.append(np.full_like(t_new, np.nan))
                continue
            out.append(np.interp(t_new, t[mask], a[mask]))
        return t_new, tuple(out)

    def _compute_speed_kmh(t, vel_mps, dist_m):
        """
        Prend velocity_smooth si dispo; sinon gradient(distance, temps).
        Renvoie vitesse en km/h.
        """
        if vel_mps is not None and len(vel_mps) == len(t):
            v = np.asarray(vel_mps, dtype=float)
        elif (dist_m is not None) and (t is not None) and len(dist_m) == len(t) and len(t) > 1:
            # dérivée numérique robuste (gradient sur temps non uniforme)
            dt = np.diff(t, prepend=t[0])
            dt[dt == 0] = np.nan
            v = np.gradient(np.asarray(dist_m, dtype=float), np.asarray(t, dtype=float))
            # gradient gère déjà les pas irréguliers; garde v en m/s
        else:
            return None
        return v * 3.6  # m/s -> km/h

    out = []
    activities = client.get_activities(limit=number_of_activity)

    for act in activities:
        try:
            streams = client.get_activity_streams(
                act.id,
                types=["time", "distance", "velocity_smooth", "heartrate"],
                resolution=resolution,
                series_type=series_type
            )
        except Exception:
            continue

        t   = np.array(streams["time"].data) if streams and "time" in streams else None
        dist= np.array(streams["distance"].data) if streams and "distance" in streams else None
        vel = np.array(streams["velocity_smooth"].data) if streams and "velocity_smooth" in streams else None
        hr  = np.array(streams["heartrate"].data) if streams and "heartrate" in streams else None

        # Sécurité longueurs / temps croissant
        if t is None or len(t) < 2:
            # Figures vides mais titrées
            title = getattr(act, "name", "Activity")
            fig_hr = plt.figure()
            plt.title(f"{title} – Heart rate")
            plt.text(0.5, 0.5, "No time stream", ha="center", va="center", transform=plt.gca().transAxes)

            fig_speed = plt.figure()
            plt.title(f"{title} – Speed")
            plt.text(0.5, 0.5, "No time stream", ha="center", va="center", transform=plt.gca().transAxes)

            out.append((title, fig_hr, fig_speed))
            continue

        # Vitesse km/h (même si pas de velocity_smooth)
        speed_kmh = _compute_speed_kmh(t, vel, dist)

        # Winsorize (suppression des extrêmes) + clips physiologiques
        if hr is not None:
            hr = _winsorize(hr, winsor_pct)
            if clip_hr_range:
                hr = np.clip(hr, clip_hr_range[0], clip_hr_range[1])

        if speed_kmh is not None:
            speed_kmh = _winsorize(speed_kmh, winsor_pct)
            if clip_speed_range:
                speed_kmh = np.clip(speed_kmh, clip_speed_range[0], clip_speed_range[1])

        # Recalage sur grille uniforme 1 Hz (MCP: comparabilité inter-séances)
        t_u, (hr_u, spd_u) = _resample_to_uniform_time(t, hr, speed_kmh, hz=resample_hz)

        # Lissage (fenêtre en secondes -> en samples)
        win = max(1, int(round(smooth_win_s * resample_hz)))
        if hr_u is not None:
            hr_u = _moving_avg(hr_u, win)
        if spd_u is not None:
            spd_u = _moving_avg(spd_u, win)

        # Masquage des pauses (vitesse très faible)
        if spd_u is not None:
            pause_mask = spd_u < float(min_speed_kmh)
        else:
            pause_mask = None

        # Figures — FC (rouge), Vitesse (bleue) — pas de subplots
        title = getattr(act, "name", "Activity")

        # Figure 1: Heart rate
        fig_hr = plt.figure()
        if hr_u is not None and t_u is not None and len(hr_u) == len(t_u):
            if pause_mask is not None:
                # On grise implicitement via NaN pendant les pauses (continuité visuelle MCP)
                hr_plot = hr_u.copy()
                hr_plot[pause_mask] = np.nan
                plt.plot(t_u, hr_plot, color="red")
            else:
                plt.plot(t_u, hr_u, color="red")
            plt.xlabel("Time (s)")
            plt.ylabel("Heart rate (bpm)")
            plt.title(f"{title} – Heart rate")
        else:
            plt.title(f"{title} – Heart rate")
            plt.text(0.5, 0.5, "No heart rate stream", ha="center", va="center", transform=plt.gca().transAxes)

        # Figure 2: Speed
        fig_speed = plt.figure()
        if spd_u is not None and t_u is not None and len(spd_u) == len(t_u):
            spd_plot = spd_u.copy()
            # On montre les pauses (valeurs faibles) telles quelles pour MCP
            plt.plot(t_u, spd_plot, color="blue")
            plt.xlabel("Time (s)")
            plt.ylabel("Speed (km/h)")
            plt.title(f"{title} – Speed")
        else:
            plt.title(f"{title} – Speed")
            plt.text(0.5, 0.5, "No speed stream", ha="center", va="center", transform=plt.gca().transAxes)

        out.append((title, fig_hr, fig_speed))

    return out

if __name__ == "__main__":
    figs = figures_speed_hr_by_activity(client, number_of_activity=3)
    for i, (title, fig_hr, fig_speed) in enumerate(figs, 1):
        fig_hr.savefig(f"activity_{i}_hr.png")
        fig_speed.savefig(f"activity_{i}_speed.png")
        plt.close(fig_hr)
        plt.close(fig_speed)
    print("Figures saved as activity_1_hr.png, activity_1_speed.png, etc.")