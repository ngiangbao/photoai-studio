package com.ngiangbao.photoaistudio.ui

import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

private object Routes {
    const val HOME = "home"
    const val EDITOR = "editor"
    const val SETTINGS = "settings"
}

/**
 * ui/PhotoAiStudioNavHost.kt - Dieu huong giua 3 man hinh, tuong duong voi viec chuyen doi
 * giua man hinh chinh va hop thoai Cai dat (SettingsDialog) trong ui/main_window.py ben
 * desktop. Mot AppViewModel duy nhat duoc dung chung cho ca app (scope theo Activity) de
 * trang thai anh da chon / ket qua AI khong mat khi dieu huong qua lai.
 */
@Composable
fun PhotoAiStudioNavHost() {
    val navController: NavHostController = rememberNavController()
    val viewModel: AppViewModel = viewModel()

    NavHost(navController = navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) {
            HomeScreen(
                viewModel = viewModel,
                onPhotoSelected = { navController.navigate(Routes.EDITOR) },
                onOpenSettings = { navController.navigate(Routes.SETTINGS) },
            )
        }
        composable(Routes.EDITOR) {
            EditorScreen(
                viewModel = viewModel,
                onBack = { navController.popBackStack() },
            )
        }
        composable(Routes.SETTINGS) {
            SettingsScreen(
                viewModel = viewModel,
                onBack = { navController.popBackStack() },
            )
        }
    }
}
