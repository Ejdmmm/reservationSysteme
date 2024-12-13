import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

class ReservationSystem:
    def __init__(self, root):
        self.root = root
        self.role = None
        self.movie_name = None
        self.reserved_seats = set()

        self.root.configure(bg="#1e1e1e")  # Temné pozadí pro kino atmosféru
        self.main_frame = tk.Frame(root, bg="#1e1e1e")
        self.main_frame.pack(padx=20, pady=20)

        self.load_movies()
        self.show_role_selection()

    def show_role_selection(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Vyberte roli:", font=("Arial", 24, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        
        tk.Button(self.main_frame, text="Admin", command=self.admin_login, bg="#ffcc66", width=20, height=2, relief="raised").pack(pady=10)
        tk.Button(self.main_frame, text="User", command=self.user_menu, bg="#66ccff", width=20, height=2, relief="raised").pack(pady=10)

    def admin_login(self):
        password = simpledialog.askstring("Heslo", "Zadejte heslo pro Admina:", show="*")
        if password == "Admin123":
            self.role = "Admin"
            self.admin_menu()
        else:
            messagebox.showerror("Chyba", "Špatné heslo!")

    def admin_menu(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Admin Menu", font=("Arial", 24, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)

        tk.Button(self.main_frame, text="Přidat film", command=self.add_movie, bg="#66ff66", width=20, height=2, relief="raised").pack(pady=10)

        for movie in self.load_movies():
            tk.Button(self.main_frame, text=f"Rezervace pro {movie}", command=lambda m=movie: self.open_reservation(m, "Admin"), bg="#ff9966", width=20, height=2, relief="raised").pack(pady=5)
            tk.Button(self.main_frame, text=f"Smazat {movie}", command=lambda m=movie: self.delete_movie(m), bg="#ff6666", width=20, height=2, relief="raised").pack(pady=5)

        tk.Button(self.main_frame, text="Zpět k přehledu", command=self.show_role_selection, bg="#ff9999", width=20, height=2, relief="raised").pack(pady=10)

    def user_menu(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Vyberte film:", font=("Arial", 24, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)

        for movie in self.load_movies():
            tk.Button(self.main_frame, text=movie, command=lambda m=movie: self.open_reservation(m, "User"), bg="#66ccff", width=20, height=2, relief="raised").pack(pady=10)

        tk.Button(self.main_frame, text="Zpět k přehledu", command=self.show_role_selection, bg="#ff9999", width=20, height=2, relief="raised").pack(pady=10)

    def open_reservation(self, movie_name, role):
        self.movie_name = movie_name
        self.role = role
        self.reserved_seats = set()
        self.load_reservations()

        self.clear_frame()
        
        # Přidání plátna
        self.add_screen()

        self.info_label = tk.Label(self.main_frame, text=f"Rezervace: {self.movie_name}", font=("Arial", 20, "bold"), fg="white", bg="#1e1e1e")
        self.info_label.pack(pady=10)

        self.seat_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.seat_frame.pack(pady=10)
        self.create_seat_grid()

        if self.role == "Admin":
            self.add_admin_controls()

        # Přidání tlačítka pro zpět do přehledu filmů
        tk.Button(self.main_frame, text="Zpět k přehledu filmů", command=self.user_menu if self.role == "User" else self.admin_menu, bg="#ffcc99", width=20, height=2, relief="raised").pack(pady=10)

    def add_screen(self):
        # Plátno (screen) nad rezervacemi
        screen_frame = tk.Frame(self.main_frame, bg="black", width=600, height=100)
        screen_frame.pack(pady=20)
        screen_label = tk.Label(screen_frame, text="PLÁTNO", font=("Arial", 20, "bold"), fg="white", bg="black")
        screen_label.pack(pady=30)

    def add_admin_controls(self):
        self.delete_button = tk.Button(self.main_frame, text="Zrušit sedadlo", command=self.delete_seat, bg="#ffcc66", width=20, height=2, relief="raised")
        self.delete_button.pack(pady=10)

        self.delete_all_button = tk.Button(self.main_frame, text="Zrušit všechny rezervace", command=self.delete_all_reservations, bg="#ff6666", width=20, height=2, relief="raised")
        self.delete_all_button.pack(pady=10)

        self.seat_label = tk.Label(self.main_frame, text="Zadejte číslo sedadla k zrušení:", bg="#1e1e1e", fg="white", font=("Arial", 12))
        self.seat_label.pack(pady=5)
        
        self.seat_entry = tk.Entry(self.main_frame, width=20, font=("Arial", 12))
        self.seat_entry.pack(pady=5)

    def create_seat_grid(self):
        self.seat_buttons = []
        for i in range(5):  # 5 řad
            row_buttons = []
            for j in range(10):  # 10 sloupců
                index = i * 10 + j
                button = tk.Button(self.seat_frame, text=f"Sedadlo {index + 1}",
                    command=lambda idx=index: self.toggle_seat(idx), width=10, height=2, font=("Arial", 10), bg="#d3d3d3", relief="raised")
                button.grid(row=i, column=j, padx=5, pady=5)
                if index in self.reserved_seats:
                    button.config(bg="red", text=f"{index + 1}", state="disabled")
                row_buttons.append(button)
            self.seat_buttons.append(row_buttons)

    def toggle_seat(self, index):
        row = index // 10
        button = self.seat_buttons[row][index % 10]

        if button["state"] == "disabled":
            if self.role == "Admin":
                self.cancel_reservation(index)
                button["state"] = "normal"
                button["text"] = f"Sedadlo {index + 1}"
                button.config(bg="#d3d3d3")
                self.info_label.config(text=f"Sedadlo {index + 1} zrušeno.")
        else:
            self.reserve_seat(index)

    def reserve_seat(self, index):
        row = index // 10
        button = self.seat_buttons[row][index % 10]
        button["state"] = "disabled"
        button["text"] = f"{index + 1}"  # Ukáže číslo sedadla
        button.config(bg="red")
        self.reserved_seats.add(index)
        self.save_reservations()
        self.info_label.config(text=f"Sedadlo {index + 1} rezervováno.")

    def cancel_reservation(self, index):
        self.reserved_seats.remove(index)
        self.save_reservations()
        self.update_seat_grid()

    def delete_seat(self):
        if self.role != "Admin":
            return  # Only Admin can delete
        try:
            seat_number = int(self.seat_entry.get()) - 1
            if seat_number in self.reserved_seats:
                self.cancel_reservation(seat_number)
                self.info_label.config(text=f"Sedadlo {seat_number + 1} zrušeno.")
            else:
                messagebox.showwarning("Chyba", f"Sedadlo {seat_number + 1} není rezervováno.")
        except ValueError:
            messagebox.showerror("Chyba", "Zadejte platné číslo sedadla.")

    def delete_all_reservations(self):
        if self.role != "Admin":
            return  # Only Admin can delete all reservations
        if messagebox.askyesno("Potvrzení", "Opravdu chcete zrušit všechny rezervace?"):
            self.reserved_seats.clear()
            self.save_reservations()
            self.update_seat_grid()
            self.info_label.config(text="Všechny rezervace byly zrušeny.")

    def delete_movie(self, movie_name):
        if self.role != "Admin":
            return  # Only Admin can delete a movie
        movies = self.load_movies()
        if movie_name in movies:
            if messagebox.askyesno("Potvrzení", f"Opravdu chcete smazat film '{movie_name}'?"):
                movies.remove(movie_name)
                self.save_movies(movies)
                messagebox.showinfo("Úspěch", f"Film '{movie_name}' byl odstraněn.")
                self.admin_menu()
        else:
            messagebox.showerror("Chyba", "Film nebyl nalezen.")

    def load_reservations(self):
        filename = f"{self.movie_name}_reservations.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.reserved_seats = set(json.load(f))

    def save_reservations(self):
        filename = f"{self.movie_name}_reservations.json"
        with open(filename, "w") as f:
            json.dump(list(self.reserved_seats), f)

    def update_seat_grid(self):
        for i, row_buttons in enumerate(self.seat_buttons):
            for j, button in enumerate(row_buttons):
                seat_index = i * 10 + j
                if seat_index in self.reserved_seats:
                    button.config(bg="red", text=f"{seat_index + 1}", state="disabled")
                else:
                    button.config(bg="#d3d3d3", text=f"Sedadlo {seat_index + 1}", state="normal")

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def add_movie(self):
        movie_name = simpledialog.askstring("Přidat film", "Zadejte název filmu:")
        if movie_name:
            movies = self.load_movies()
            movies.append(movie_name)
            self.save_movies(movies)
            messagebox.showinfo("Úspěch", f"Film '{movie_name}' byl přidán.")

    def load_movies(self):
        if os.path.exists("movies.json"):
            with open("movies.json", "r") as f:
                return json.load(f)
        return []

    def save_movies(self, movies):
        with open("movies.json", "w") as f:
            json.dump(movies, f)

def main():
    root = tk.Tk()
    root.title("Rezervační systém")
    root.geometry("600x600")
    ReservationSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
