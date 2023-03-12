"""立体四目並べのベースモジュール"""
from __future__ import annotations
import os
import csv
from enum import Enum

import numpy as np


class BallType(Enum):
    """設置するボールの列挙型定数
    """
    DRAW = -2
    INVALID = -1
    PLAYER1 = 0
    PLAYER2 = 1

    @property
    def enemy(self):
        """敵のボール定数を取得するプロパティ
           プレーヤー以外の場合は自身を取得する

        Returns:
            _type_: 敵のボール定数
        """
        if self == BallType.PLAYER1:
            return BallType.PLAYER2
        elif self == BallType.PLAYER2:
            return BallType.PLAYER1
        else:
            return self


class Board:
    """立体四目並べのボードクラス
    """
    def __init__(self) -> None:
        self._log = []
        self._player = BallType.PLAYER1
        self._winner = BallType.INVALID
        self._board_data = np.array([[[BallType.INVALID for _ in range(self.board_size)] for _ in range(self.board_size)] for _ in range(self.board_size)])
        self._reach_data = np.array([[[[BallType.INVALID for _ in range(self.number_of_players)] for _ in range(self.board_size)] for _ in range(self.board_size)] for _ in range(self.board_size)])

    @property
    def board_size(self) -> int:
        """ボードのサイズを取得するプロパティ

        Returns:
            int: ボードのサイズ
        """
        return 4

    @property
    def number_of_players(self) -> int:
        """プレーヤー数を取得するプロパティ

        Returns:
            int: プレーヤー数
        """
        return 2

    @property
    def player(self) -> BallType:
        """現在の手番のプレーヤーを取得するプロパティ

        Returns:
            BallType: 手番のプレーヤー
        """
        return self._player

    @property
    def color_code_per_player(self) -> float:
        """プレーヤーごとのカラーコード計算用数値を取得するプロパティ

        Returns:
            float: カラーコード計算用数値
        """
        return 1 / (self.number_of_players + 1)

    @property
    def winner(self) -> BallType:
        """勝者を取得するプロパティ
           ゲームが終了するまではBallType.INVALIDを返す

        Returns:
            BallType: 勝者
        """
        return self._winner

    @property
    def board_data(self) -> np.ndarray:
        """現在のボードの状態を取得するプロパティ

        Returns:
            np.ndarray: ボードの状態
        """
        return self._board_data

    @property
    def reach_data(self) -> np.ndarray:
        """現在のボードのリーチの状態を取得するプロパティ

        Returns:
            np.ndarray: リーチの状態
        """
        return self._reach_data

    def board_put(self, x: int, y: int) -> bool:
        """指定された座標にボールを設置するメソッド

        Args:
            x (int): X座標
            y (int): Y座標

        Returns:
            bool: 設置が行えたかの真理値
        """
        try:
            for z, v in enumerate(self.board_data[x, y, :]):
                if v == BallType.INVALID:
                    self._board_data[x, y, z] = self.player
                    self._board_check()
                    self._log.append(f'{x}, {y}')
                    self._player = self.player.enemy
                    return True
            return False
        except IndexError:
            return False

    def random_put(self) -> None:
        """ランダムに設置するメソッド
        """
        while True:
            x, y = np.random.randint(self.board_size), np.random.randint(self.board_size)
            if self.board_put(x, y):
                break

    def _board_check(self) -> None:
        if len([True for x in range(self.board_size) for y in range(self.board_size) for z in range(self.board_size) if self.board_data[x, y, z] == BallType.INVALID]) == 0:
            self._winner = BallType.DRAW
        tmp = np.array([i for i in range(self.board_size)] + [i for i in range(self.board_size - 2, -1, -1)])
        for x, y, z in np.array([[0, 0, 0], [0, 0, self.board_size - 1], [0, self.board_size - 1, self.board_size - 1], [self.board_size - 1, 0, self.board_size - 1]]):
            count = [True if self.player == self.board_data[tmp[x + i], tmp[y + i], tmp[z + i]] else False for i in range(self.board_size)]
            if self.board_size == count.count(True):
                self._winner = self.player
            elif self.board_size - 1 == count.count(True):
                i = count.index(False)
                self._reach_data[tmp[x + i], tmp[y + i], tmp[z + i], self.player.value] = self.player
        for i in np.arange(self.board_size):
            for t0, t1, in np.array([[0, 0], [0, self.board_size - 1]]):
                count = [True if self.player == self.board_data[i, tmp[t0 + j], tmp[t1 + j]] else False for j in range(self.board_size)]
                if self.board_size == count.count(True):
                    self._winner = self.player
                elif self.board_size - 1 == count.count(True):
                    j = count.index(False)
                    self._reach_data[i, tmp[t0 + j], tmp[t1 + j], self.player.value] = self.player
                count = [True if self.player == self.board_data[tmp[t0 + j], i, tmp[t1 + j]] else False for j in range(self.board_size)]
                if self.board_size == count.count(True):
                    self._winner = self.player
                elif self.board_size - 1 == count.count(True):
                    j = count.index(False)
                    self._reach_data[tmp[t0 + j], i, tmp[t1 + j], self.player.value] = self.player
                count = [True if self.player == self.board_data[tmp[t0 + j], tmp[t1 + j], i] else False for j in range(self.board_size)]
                if self.board_size == count.count(True):
                    self._winner = self.player
                elif self.board_size - 1 == count.count(True):
                    j = count.index(False)
                    self._reach_data[tmp[t0 + j], tmp[t1 + j], i, self.player.value] = self.player
        for i in range(self.board_size):
            for j in range(self.board_size):
                count = [True if self.player == bd else False for bd in self.board_data[i, j, :]]
                if self.board_size == count.count(True):
                    self._winner = self.player
                elif self.board_size - 1 == count.count(True):
                    k = count.index(False)
                    self._reach_data[i, j, k, self.player.value] = self.player
                count = [True if self.player == bd else False for bd in self.board_data[i, :, j]]
                if self.board_size == count.count(True):
                    self._winner = self.player
                elif self.board_size - 1 == count.count(True):
                    k = count.index(False)
                    self._reach_data[i, k, j, self.player.value] = self.player
                count = [True if self.player == bd else False for bd in self.board_data[:, i, j]]
                if self.board_size == count.count(True):
                    self._winner = self.player
                elif self.board_size - 1 == count.count(True):
                    k = count.index(False)
                    self._reach_data[k, i, j, self.player.value] = self.player

    def board_reset(self) -> None:
        """ボードの状態を初期化するメソッド
        """
        self._log = []
        self._player = BallType.PLAYER1
        self._winner = BallType.INVALID
        self._board_data = np.array([[[BallType.INVALID for _ in range(self.board_size)] for _ in range(self.board_size)] for _ in range(self.board_size)])
        self._reach_data = np.array([[[[BallType.INVALID for _ in range(self.number_of_players)] for _ in range(self.board_size)] for _ in range(self.board_size)] for _ in range(self.board_size)])

    def write_log(self) -> None:
        """ゲームのログをファイルに書き込むメソッド
        """
        if os.path.isfile('log.csv'):
            with open('log.csv', mode='a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([self.winner.value] + self._log)
        else:
            with open('log.csv', mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([self.winner.value] + self._log)

    def read_log(self) -> list[list[str]]:
        """ゲームのログを読み込むメソッド

        Returns:
            _type_: 全てをゲームのログ
        """
        if os.path.isfile('log.csv'):
            with open('log.csv', mode='r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                logs = [row for row in reader]
            return logs

    def random_execution(self, count=100):
        """ランダムに設置し学習用のデータを作成するメソッド

        Args:
            count (int, optional): 実行する回数. デフォルトは100.
        """
        for _ in range(count):
            while self.winner == BallType.INVALID:
                self.random_put()
            self.write_log()
            self.board_reset()

if __name__ == '__main__':
    Board().random_execution()
